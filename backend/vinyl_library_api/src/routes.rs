use mysql::prelude::*;
use mysql::*;
use rocket::data::{Data, ToByteUnit};
use rocket::fs::NamedFile;
use rocket::serde::json::Json;
use serde::Deserialize;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use crate::artist::Artist;
use crate::database::connect;
use crate::vinyl::Vinyl;

const IMAGES_DIRECTORY: &str = r"E:\python_projects\vinyl_library";

// [ARTISTS] =======================================================================================

#[get("/artists")]
pub fn list_all_artists() -> Json<Vec<Artist>> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    return Json(
        conn.query_map("SELECT * FROM artists;", |mut row: mysql::Row| Artist {
            id: row.take("id").unwrap(),
            name: row.take("name").unwrap(),
        })
        .expect("Failed to query all artists"),
    );
}

#[post("/artists", data = "<name>")]
pub fn add_artist(name: Json<String>) -> Json<Artist> {
    let name = name.replace('"', "");
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let existing_id: Option<u32> = conn
        .query_first(format!(
            "SELECT id FROM vinyl_library.artists WHERE name = \"{}\";",
            name
        ))
        .expect("Failed to get existing name");

    if existing_id.is_some() {
        return Json(Artist {
            id: existing_id.unwrap() as u32,
            name,
        });
    }

    let stmt = conn
        .prep("INSERT INTO vinyl_library.artists (name) VALUES (:name)")
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(stmt, params! {"name" => &name})
        .expect("Failed to insert new artist");

    return Json(Artist {
        id: conn.last_insert_id() as u32,
        name,
    });
}

fn check_artist_by_id(mut conn: PooledConn, id: &u32) -> (PooledConn, Option<u32>) {
    let existing_artist_id: Option<u32> = conn
        .query_first(format!(
            "SELECT id FROM vinyl_library.artists WHERE id = '{}';",
            id
        ))
        .expect("Failed to get existing name");
    match existing_artist_id {
        Some(i) => (conn, Some(i)),
        _ => (conn, None),
    }
}

#[get("/artists/list_vinyls?<id>")]
pub fn list_vinyls_for_artist(id: u32) -> Json<Vec<Vinyl>> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    return Json(
        conn.query_map(
            format!(
                r#"SELECT
                    vinyls.id,
                    vinyls.name,
                    vinyls.artist_id,
                    artists.name AS artist_name,
                    vinyls.added_date,
                    vinyls.cover_file_name
                FROM vinyls
                LEFT JOIN artists ON vinyls.artist_id = artists.id
                WHERE vinyls.artist_id = {};"#,
                id
            ),
            |mut row: mysql::Row| Vinyl {
                id: row.take("id").unwrap(),
                name: row.take("name").unwrap(),
                artist_id: row.take("artist_id").unwrap(),
                artist_name: row.take("artist_name").unwrap(),
                added_date: row.take("added_date").unwrap(),
                cover_file_name: row.get("cover_file_name").unwrap(),
            },
        )
        .expect("Failed to query all vinyls"),
    );
}

#[post("/artists/delete?<id>")]
pub fn delete_artist(id: u32) {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let (mut conn, existing_artist_id) = check_artist_by_id(conn, &id);
    if existing_artist_id.is_none() {
        panic!("{} is not a valid artist id", &id);
    }

    let stmt = conn
        .prep("DELETE FROM `vinyl_library`.`artists` WHERE (`id` = :id);")
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(stmt, params! { "id" => id})
        .expect("Failed to delete artist");
}

#[post("/artists/update?<id>", data = "<new_name>")]
pub fn update_artist(id: u32, new_name: String) -> Json<Artist> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let (mut conn, existing_artist_id) = check_artist_by_id(conn, &id);
    if existing_artist_id.is_none() {
        panic!("{} is not a valid artist id", &id);
    }

    let stmt = conn
        .prep("UPDATE vinyl_library.artists SET name = :name WHERE id = :id;")
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(stmt, params! { "name" => &new_name, "id" => id })
        .expect("Failed to update vinyl");

    Json(Artist { id, name: new_name })
}

// [VINYLS] ========================================================================================

#[get("/vinyls")]
pub fn list_all_vinyls() -> Json<Vec<Vinyl>> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    return Json(
        conn.query_map(
            r#"SELECT
				vinyls.id,
				vinyls.name,
				vinyls.artist_id,
				artists.name AS artist_name,
				vinyls.added_date,
				vinyls.cover_file_name
			FROM vinyls
			LEFT JOIN artists ON vinyls.artist_id = artists.id;"#,
            |mut row: mysql::Row| Vinyl {
                id: row.take("id").unwrap(),
                name: row.take("name").unwrap(),
                artist_id: row.take("artist_id").unwrap(),
                artist_name: row.take("artist_name").unwrap(),
                added_date: row.take("added_date").unwrap(),
                cover_file_name: row.get("cover_file_name").unwrap(),
            },
        )
        .expect("Faild to query all vinyls"),
    );
}

#[derive(Deserialize, Debug)]
pub struct VinylUserData {
    name: String,
    artist_id: u32,
    artist_name: String,
    cover_file_name: String,
}

#[post("/vinyls", format = "json", data = "<data>")]
pub fn add_vinyl(data: Json<VinylUserData>) -> Json<Vinyl> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let existing_vinyl = conn
        .query_first(format!(
            "SELECT
				vinyls.id,
				vinyls.name,
				vinyls.artist_id,
				artists.name AS artist_name,
				vinyls.added_date,
				vinyls.cover_file_name
			FROM vinyls
			LEFT JOIN artists ON vinyls.artist_id = artists.id
			WHERE vinyls.name = \"{}\";",
            &data.name
        ))
        .map(|row: Option<mysql::Row>| match row {
            Some(mut r) => Some(Vinyl {
                id: r.take("id").unwrap(),
                name: r.take("name").unwrap(),
                artist_id: r.take("artist_id").unwrap(),
                artist_name: r.take("artist_name").unwrap(),
                added_date: r.take("added_date").unwrap(),
                cover_file_name: r.get("cover_file_name").unwrap(),
            }),
            _ => None,
        })
        .expect("Failed to get existing name");
    if existing_vinyl.is_some() {
        return Json(existing_vinyl.unwrap());
    }

    let (mut conn, existing_artist_id) = check_artist_by_id(conn, &data.artist_id);
    if existing_artist_id.is_none() {
        panic!("{} is not a valid artist id", &data.artist_id);
    }

    let start = SystemTime::now();
    let since_the_epoch = start
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_secs() as u32;

    let stmt = conn
        .prep(
            r#"INSERT INTO vinyl_library.vinyls (name, artist_id, added_date, cover_file_name)
        VALUES (:name, :artist_id, :added_date, :cover_file_name)"#,
        )
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(
        stmt,
        params! {
            "name" => &data.name,
            "artist_id" => &data.artist_id,
            "added_date" => &since_the_epoch,
            "cover_file_name" => &data.cover_file_name
        },
    )
    .expect("Failed to insert new artist");

    return Json(Vinyl {
        id: conn.last_insert_id() as u32,
        name: data.name.clone(),
        artist_id: data.artist_id.clone(),
        artist_name: data.artist_name.clone(),
        added_date: since_the_epoch.clone(),
        cover_file_name: data.cover_file_name.clone(),
    });
}

#[post("/vinyls/update?<id>", format = "json", data = "<data>")]
pub fn update_vinyl(id: u32, data: Json<VinylUserData>) -> Json<Vinyl> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let vinyl = conn
        .query_first(format!(
            r#"SELECT
				vinyls.id,
				vinyls.name,
				vinyls.artist_id,
				artists.name AS artist_name,
				vinyls.added_date,
				vinyls.cover_file_name
			FROM vinyls
			LEFT JOIN artists ON vinyls.artist_id = artists.id
			WHERE vinyls.id = '{}'"#,
            id
        ))
        .map(|row: Option<mysql::Row>| match row {
            Some(mut r) => Some(Vinyl {
                id: r.take("id").unwrap(),
                name: r.take("name").unwrap(),
                artist_id: r.take("artist_id").unwrap(),
                artist_name: r.take("artist_name").unwrap(),
                added_date: r.take("added_date").unwrap(),
                cover_file_name: r.get("cover_file_name").unwrap(),
            }),
            _ => None,
        })
        .expect("Failed to query vinyl in the database")
        .expect(format!("There is no vinyl with the id {}", id).as_str());

    let (mut conn, existing_artist_id) = check_artist_by_id(conn, &data.artist_id);
    if existing_artist_id.is_none() {
        panic!("{} is not a valid artist id", &data.artist_id);
    }

    let stmt = conn
        .prep(
            r#"UPDATE vinyl_library.vinyls
            SET
                name = :name,
                artist_id = :artist_id,
                cover_file_name = :cover_file_name
            WHERE
                (id = :id);"#,
        )
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(
        stmt,
        params! {
            "name" => &data.name,
            "artist_id" => &data.artist_id,
            "cover_file_name" => &data.cover_file_name,
            "id" => id
        },
    )
    .expect("Failed to update vinyl");

    return Json(Vinyl {
        id,
        name: data.name.clone(),
        artist_id: data.artist_id.clone(),
        artist_name: data.artist_name.clone(),
        added_date: vinyl.added_date.clone(),
        cover_file_name: data.cover_file_name.clone(),
    });
}

#[post("/vinyls/delete?<id>")]
pub fn delete_vinyl(id: u32) {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");

    let stmt = conn
        .prep("DELETE FROM `vinyl_library`.`vinyls` WHERE (`id` = :id);")
        .expect("Failed to prepare statement");

    conn.exec::<bool, _, _>(stmt, params! { "id" => id})
        .expect("Failed to delete vinyl");
}

#[get("/vinyls/shuffle?<count>")]
pub fn shuffle_vinyls(count: u32) -> Json<Vec<Vinyl>> {
    let mut conn =
        connect().expect("Failed to establish connection with the 'vinyl_library' database");
    // SELECT * FROM vinyl_library.vinyls ORDER BY RAND() LIMIT 33;
    return Json(
        conn.query_map(
            format!(
                r#"SELECT
                    vinyls.id,
                    vinyls.name,
                    vinyls.artist_id,
                    artists.name AS artist_name,
                    vinyls.added_date,
                    vinyls.cover_file_name
                FROM vinyls
                LEFT JOIN artists ON vinyls.artist_id = artists.id
                ORDER BY RAND()
                LIMIT {};"#,
                count
            ),
            |mut row: mysql::Row| Vinyl {
                id: row.take("id").unwrap(),
                name: row.take("name").unwrap(),
                artist_id: row.take("artist_id").unwrap(),
                artist_name: row.take("artist_name").unwrap(),
                added_date: row.take("added_date").unwrap(),
                cover_file_name: row.get("cover_file_name").unwrap(),
            },
        )
        .expect("Faild to query random vinyls list"),
    );
}

// [IMAGES] ========================================================================================

#[get("/images/<image_name>")]
pub async fn get_image(image_name: PathBuf) -> Option<NamedFile> {
    NamedFile::open(Path::new(IMAGES_DIRECTORY).join(image_name))
        .await
        .ok()
}

#[get("/images")]
pub fn get_image_names() -> Json<Vec<String>> {
    if let Ok(entries) = fs::read_dir(IMAGES_DIRECTORY) {
        let image_names: Vec<String> = entries
            .map(|e| e.unwrap().file_name().to_str().unwrap().to_string())
            .collect();
        return Json(image_names);
    }
    return Json(Vec::new());
}

#[post("/images/upload/<filename>", data = "<image_data>")]
pub async fn upload_image(filename: String, image_data: Data<'_>) {
    image_data
        .open(128.kibibytes())
        .into_file(format!(r"{}\{}", IMAGES_DIRECTORY, filename))
        .await
        .ok();
}
