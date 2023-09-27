use mysql;
use std::error::Error;

pub fn connect() -> Result<mysql::PooledConn, Box<dyn Error>> {
    let url = env!("VINYL_LIBRARY_DB_URL");
    let pool = mysql::Pool::new(url)?;
    let conn = pool.get_conn()?;
    Ok(conn)
}
