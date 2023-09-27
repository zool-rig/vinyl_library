#[macro_use]
extern crate rocket;

mod artist;
mod database;
mod routes;
mod vinyl;

use rocket::{Build, Rocket};

#[launch]
fn rocket() -> Rocket<Build> {
    rocket::build().mount(
        "/vinyl_library",
        routes![
            routes::list_all_vinyls,
            routes::list_all_artists,
            routes::add_artist,
            routes::add_vinyl,
            routes::update_vinyl,
            routes::delete_vinyl,
            routes::list_vinyls_for_artist,
            routes::get_image,
            routes::delete_artist,
            routes::upload_image,
            routes::get_image_names,
        ],
    )
}
