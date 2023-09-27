use rocket::serde::Serialize;

#[derive(Debug, Serialize)]
#[serde(crate = "rocket::serde")]
pub struct Vinyl {
    pub id: u32,
    pub name: String,
    pub artist_id: u32,
    pub artist_name: String,
    pub added_date: u32,
    pub cover_file_name: String,
}
