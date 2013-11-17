var db = require('./db_commands');

function makeBadResponse(response) {
	console.error("Panik auf dem Titanik!");
	console.log("404");
	response.writeHead(404, { "Content-Type" : "text/plain" });
  response.end();
}

function list(response, query) {
  console.log("list, Q = [" + query + "]");
  if (query.type != undefined) {
  	if (query.type == 'ingredients') {
  		db.getAllIngredients(function callback(err, result) {
        if (err) {
          makeBadResponse(response);
        } else {
          response.writeHead(200, { "Content-Type" : "text/plain" });
          response.write("R = " + JSON.stringify(result));
          response.end();
        }
      });
  	} else if (query.type == 'effects') {
  		db.getAllEffects(function callback(err, result) {
        if (err) {
          makeBadResponse(response);
        } else {
          response.writeHead(200, { "Content-Type" : "text/plain" });
          response.write("R = " + JSON.stringify(result));
          response.end();
        }
      });
  	} else {
      makeBadResponse(response);
  	}
  } else {
    makeBadResponse(response);
  }
}

function info(response, query) {
  console.log("info, Q = [" + query + "]");
  if (query.type != undefined && query.name != undefined) {
  	if (query.type == 'ingredient') {
	    db.getIngredient(query.name, function callback(err, result) {
	      if (err) {
	        makeBadResponse(response);
	      } else {
	        response.writeHead(200, { "Content-Type" : "text/plain" });
	        response.write("R = " + JSON.stringify(result));
	        response.end();
	      }
	    });
  	} else if (query.type == 'effect') {
  		db.getEffect(query.name, function callback(err, result) {
  			if (err) {
  				makeBadResponse(response);
  			} else {
  				response.writeHead(200, { "Content-Type" : "text/plain" });
  				response.write("R = " + JSON.stringify(result));
  				response.end();
  			}
  		});
  	} else {
      makeBadResponse(response);
  	}
  } else {
    makeBadResponse(response);
  }
}

function mix(response, query) {
  console.log("mix, Q = [" + query + "]");
  response.writeHead(200, { "Content-Type" : "text/plain" });
  response.write("I'm alive! I need mix");
  response.end();
}

exports.list = list;
exports.info = info;
exports.mix = mix;
