/**
 * @description
 *  Fetch a image from MapBiomas collection, limited by Cerrado, by the a class.
 *  The image have the class where have the Total_Year(totalYears = 20) with same class
 * @author
 *    Luiz Motta
 * @date
 * 2021-08-09
 */

// Function Remap
var remap_biomas = function(ids, image, year){
  var f1 = function(id) { return 1; };
  var r = image.remap({
          from: ids,
          to:   ids.map( f1 ),
          bandName: 'classification_' + year
  }).rename( year.toString() ); 
  return r;
};
// Function create image
var image_class = function(label, ids, firstYear, lastYear, mb_cerrado, totalYears){
  var stack = remap_biomas( ids, mb_cerrado, firstYear );
  for (var y = firstYear + 1; y < lastYear + 1; y++){
    stack = stack.addBands( remap_biomas( ids, mb_cerrado, y ) );
  }
  var label_stable = label.concat("_stable");
  var img_stable = stack.reduce( ee.Reducer.count() ).gte( totalYears ).selfMask().rename( label_stable );
  //var img_stable = stack.reduce( ee.Reducer.count() ).gte( totalYears ).rename( label_stable );
  var label_not_stable = label.concat("_not_stable");
  var img_not_stable = stack.reduce( ee.Reducer.count() ).lt( totalYears ).selfMask().rename( label_not_stable );
  //var img_not_stable = stack.reduce( ee.Reducer.count() ).lt( totalYears ).rename( label_not_stable );
  return img_stable.addBands( [ img_stable, img_not_stable ])
  
};
// Functions
var showMap = function(layers){
  for( var id in layers ){
    Map.addLayer( layers[id].image, layers[id].params, layers[id].name );
  }
}

var exportImages = function(layers){
  for( var id in layers ){
    Export.image.toDrive({
      image: layers[id].image.toByte(),
      maxPixels: 1e13,
      shardSize: 32, // Use chunks
      description: layers[id].name,
      scale: 30,
      region: lim_cerrado.geometry().bounds(),
      fileFormat: 'GeoTIFF'
    });
  }
}

// ID Assets 
var assetId_mb5 = 'projects/mapbiomas-workspace/public/collection5/mapbiomas_collection50_integration_v1';
var assetId_biomas = 'projects/mapbiomas-workspace/AUXILIAR/biomas-2019';

// Fetch Assets
var mb_5 = ee.Image( assetId_mb5 );
var biomas = ee.FeatureCollection( assetId_biomas );

// Feature with only Cerrado.selfMask().rename( label )
var lim_cerrado = biomas.filter( ee.Filter.eq('Bioma', 'Cerrado') );

// Clip Mapbiomas by Cerrado
var mb_cerrado = mb_5.clip( lim_cerrado );

var firstYear = 1985;
var lastYear = 2019;

var idsNatural = [ 3, 4, 5, 11, 12, 13, 23, 29, 32, 33 ];
var idsAntropico = [ 9, 15, 20, 21, 24, 30, 31, 36, 39, 41 ];
var idsNaoDef = [ 25, 27 ];



var totalYears = 20;

var imgNat = image_class( 'natural', idsNatural, firstYear, lastYear, mb_cerrado, totalYears );
var imgAnt = image_class( 'antropico', idsAntropico, firstYear, lastYear, mb_cerrado, totalYears );
var imgNaoDef = image_class( 'nao_definido', idsNaoDef, firstYear, lastYear, mb_cerrado, totalYears );


var layersShow = [
  { name: 'MapBiomas', image: mb_cerrado, params: {} },
  { name: 'antropico', image: imgAnt, params: {"opacity":1,"bands":['antropico_stable'],"palette":['E974ED']} },
  { name: 'natural', image: imgNat, params: {"opacity":1,"bands":['natural_stable'],"palette":['1F4423']} }
];

var layersExport = [
  { name: 'natural', image: imgNat},
  { name: 'antropico', image: imgAnt},
  { name: 'nao_definido', image: imgNaoDef},
];

//showMap( layersShow );
//Map.addLayer( layersShow[1].image, layersShow[1].params, layersShow[1].name );
exportImages( layersExport); 
