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

function mix_smth(get_method, smth_list, res_map, response) {
	smth_list.forEach(function(value, index, array) {
		get_method(value, function(err, result) {
			if (err) {
				res_map[value] = undefined;
				makeBadResponse(response);
			} else {
				res_map[value] = result;
				console.log("%s %s", value, result);
			  if(Object.keys(res_map).length == smth_list.length) {
			  	response.writeHead(200, { "Content-Type" : "text/plain" });
  				response.write("R = " + JSON.stringify(res_map));
  				response.end();
			  }
			}
		});
	});
}

function mix(response, query) {
  console.log("mix, Q = [" + query + "]");
  var list=[];
  for (var k in query) {
  	if (k.indexOf('n') == 0) {
  		list.push(query[k]);
  	}
  }
  
  if (query.type == 'ingredients') {
  	mix_smth(db.getIngredientShort, list, {}, response);
  } else if (query.type == 'effects') {
  	mix_smth(db.getEffect, list, {}, response);
  } else {
  	makeBadResponse(response);
  }
}

exports.list = list;
exports.info = info;
exports.mix = mix;
