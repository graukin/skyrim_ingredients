function route(handle, pathname, query, response) {
  console.log("route: %s, %s", pathname, query);
  if (typeof(handle[pathname]) == 'function') {
    handle[pathname](response, query);
  } else {
    console.log("No way.");
    response.writeHead(404, {"Content-Type": "text/plain"});
    response.write("404 Not found");
    response.end();
  }
}

exports.route = route;
