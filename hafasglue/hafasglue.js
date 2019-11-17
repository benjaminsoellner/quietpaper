
const express = require('express');
const app = express();
const hafas = require('hafas-client')
const hafasDb = require('hafas-client/p/db')
const hafasClient = hafas(hafasDb, 'hafas-quietpaper-glue')

app.get('/', function(req, res) {
    res.send('Hello World!');
});

from = {
	type: 'location',
	address: 'Sattelaecker 1B, 70565 Stuttgart',
	latitude: 48.721010,
	longitude: 9.094880
}

to = {
	type: 'location',
	address: 'Rothebühlplatz, Stuttgart',
	latitude: 48.773630,
	longitude: 9.169120
}

app.get('/query', function(req, res) {
    from = {
        type: 'location',
        address: req.query.from_address,
        latitude: req.query.from_latitude,
        longitude: req.query.from_longitude
    }
    to = {
        type: 'location',
        address: req.query.to_address,
        latitude: req.query.to_latitude,
        longitude: req.query.to_longitude
    }
    opt = {
        departure: (new Date(parseInt(req.query.departure)*1000)).toISOString(),
        results: req.query.num_routes,
        via: req.query.via_station,
        stopovers: false,
        transfers: -1,
        transferTime: 0,
        accessibility: 'none',
        startWithWalking: true,
        language: 'en',
        scheduledDays: false
    }
    response = hafasClient.journeys(from, to, opt)
        .then((response) => (res.json(response.journeys)))
        .catch((response) => (res.json(response.journeys)));
});

app.listen(3333, 'localhost', function () {
  console.log('Started hafas-glue on to listen on localhost:3000.');
});