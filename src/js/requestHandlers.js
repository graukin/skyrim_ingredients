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

function mix_smth(mix_method, smth_list, res_map, final_method, response) {
	smth_list.forEach(function(value, index, array) {
		mix_method(value, function(err, result) {
			if (err) {
				res_map[value] = undefined;
				makeBadResponse(response);
			} else {
				res_map[value] = result.effects;
			  if(Object.keys(res_map).length == smth_list.length) {
			    final_method(res_map, response);
			  }
			}
		});
	});
}

function mix_ingredients(map, response) {
	var map_keys = Object.keys(map);
	var effects={};
	Object.keys(map).forEach(function (value, index, array){
		map[value].forEach(function(value, index, array) {
			if (value in effects) {
				effects[value] = effects[value] + 1;
			} else {
				effects[value] = 1;
			}
		});
		map_keys.shift();
		if (map_keys.length === 0) {
			var res = "";
			var effects_keys = Object.keys(effects);
			Object.keys(effects).forEach(function(value, index, array) {
				if (effects[value] > 1) {
					res = res + " + " + value;
				}
				effects_keys.shift();
				if (effects_keys.length === 0) {
					if (res.length === 0) {
						makeBadResponse(response);
					} else {
						response.writeHead(200, { "Content-Type" : "text/plain" });
						response.write("I have something: " + res.substring(3, res.length));
						response.end();
					}
				}
			});
		}
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
  	mix_smth(db.getIngredient, list, {}, mix_ingredients, response);
  } else if (query.type == 'effects') {
  	
  } else {
  	makeBadResponse(response);
  }
}

exports.list = list;
exports.info = info;
exports.mix = mix;
