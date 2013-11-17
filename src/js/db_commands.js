var r = require('rethinkdb'),
    assert = require('assert');

var dbConfig = {
  host  : process.env.RDB_HOST || 'localhost',
  port  : parseInt(process.env.RDB_PORT) || 28015,
  db    : process.env.RDB_DB || 'games',
  table : 'skyrim_ingredients'
};

// get list of all ingredients
function getAllIngredients(callback) {
	var functionName = "getAllIngredients";
	console.info("db.getAllIngredient");
	onConnect(function (err, connection) {
		console.info("[INFO ][%s][%s]", connection['_id'], functionName);
		
		r.db(dbConfig.db).table(dbConfig.table).pluck('name', 'dlc').orderBy(r.asc('name')).run(connection, function(err, cursor) {
			if (err) {
				console.error("[ERROR][%s][%s] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
				callback(err);
			} else {
				cursor.toArray(function(err, list) {
					if (err) {
						console.error("[ERROR][%s][%s] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
						callback(err);
					} else {
						callback(null, list);
					}
					connection.close();
				});
			}
		});
	});
}

// get list of all effects
function getAllEffects(callback) {
	var functionName = "getAllEffects";
	console.info("db.getAllEffects");
	onConnect(function (err, connection) {
		console.info("[INFO ][%s][%s]", connection['_id'], functionName);
		
		r.db(dbConfig.db).table(dbConfig.table).concatMap(function(ingr) { return ingr('effects'); }).distinct().run(connection, function(err, cursor) {
			if (err) {
				console.error("[ERROR][%s][%s] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
				callback(err);
			} else {
				cursor.toArray(function(err, list) {
					if (err) {
						console.error("[ERROR][%s][%s] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
						callback(err);
					} else {
						callback(null, list);
					}
					connection.close();
				});
			}
		});
	});
}

// get ingredient by name
function getIngredient(name, callback) {
	var functionName = "getIngredient (" + name + ")";
  console.info("db.getIngredient(%s);", name);
  onConnect(function (err, connection) {
    console.info("[INFO ][%s][%s] %s", connection['_id'], functionName, name);

    r.db(dbConfig.db).table(dbConfig.table).filter({'name': name}).limit(1).run(connection, function(err, cursor) {
      if(err) {
        console.error("[ERROR][%s][%s][collect] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
        callback(err);
      } else {
        cursor.next(function (err, row) {
          if(err) {
            console.error("[ERROR][%s][%s][collect] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
            callback(err);
          } else {
            callback(null, row);
          }
          connection.close();
        });
      }
    });
  });
}

// get effect by name
function getEffect(name, callback) {
	var functionName = "getEffect (" + name + ")";
  console.info("db.getEffect(%s);", name);
  onConnect(function (err, connection) {
    console.info("[INFO ][%s][%s] %s", connection['_id'], functionName, name);

    r.db(dbConfig.db).table(dbConfig.table).filter(r.row('effects').contains(name)).pluck('name', 'dlc').orderBy(r.asc('name')).run(connection, function(err, cursor) {
      if(err) {
        console.error("[ERROR][%s][%s][collect] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
        callback(err);
      } else {
        cursor.toArray(function (err, list) {
          if(err) {
            console.error("[ERROR][%s][%s][collect] %s:%s\n%s", connection['_id'], functionName, err.name, err.msg, err.message);
            callback(err);
          } else {
            callback(null, list);
          }
          connection.close();
        });
      }
    });
  });
}

function onConnect(callback) {
  r.connect({ host : dbConfig.host, port : dbConfig.port}, function(err, connection) {
    assert.ok(err == null, err);
    connection['_id'] = Math.floor(Math.random() * 10001);
    callback(err, connection);
  });
}

exports.getAllIngredients = getAllIngredients;
exports.getAllEffects = getAllEffects;
exports.getIngredient = getIngredient;
exports.getEffect = getEffect;