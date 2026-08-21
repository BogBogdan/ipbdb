$(document).ready(function(){
    base_url = 'http://servo.aob.rs/emol';
    colltypes = 'select[name=CollisionTypes]';
    species = 'select[name=Species]';
    states = 'select[name=SpeciesStates]'; 
    cstypes = 'select[name=CrossSectionTypes]';

    $(colltypes + ' option:eq(0)').prop('selected','selected');
    $(species).resetElem();
    $(states).resetElem();
    $(cstypes).resetElem();

    $(colltypes).change(function(){
        coll_type_id = $(this).val();
//        $(species, states, cstypes).resetElem();
        $(species).resetElem();
        $(states).resetElem();
        $(cstypes).resetElem();
        $(species).removeAttr('disabled');
	request_url = base_url + '/get_species/' + coll_type_id + '/';
	$.getJSON( request_url, function(data){
                $.each(data, function(key, value){
                    $(species).append('<option value="' + key + '">' + value +'</option>');
		});
        })
    }) 

    $(species).change(function(){
        species_id = $(this).val();
	coll_type_id = $(colltypes).val();
        $(states).resetElem();
        $(cstypes).resetElem();
	$(states).removeAttr('disabled');
	request_url = base_url + '/get_states/' + species_id + '/' + coll_type_id + '/';
	$.getJSON( request_url, function(data){
		$.each(data, function(key, value){
                    $(states).append('<option value="' + key + '">' + value +'</option>');
                });
	})
    }) 

    $(states).change(function(){
        state_id = $(this).val();
        coll_type_id = $(colltypes).val();
        $(cstypes).resetElem();
        $(cstypes).removeAttr('disabled');
        request_url = base_url + '/get_cs_types/'  + state_id + '/'  + coll_type_id + '/';
        $.getJSON( request_url, function(data){
                $.each(data, function(key, value){
                    $(cstypes).append('<option value="' + key + '">' + value +'</option>');
                });
        })
    }) 
    
    $('#generateXsams').click(function() {
        xsamsDoc = null;
        var searchString = "select * ";
	if ($(colltypes).val()!='') {
           searchString += "where CollisionIAEACode='" + $(colltypes).val() + "' ";
	   if ($(species).val()!='') {
	      searchString += "and InchiKey='" + $(species).val() + "' ";
	   }
	}
	   var str = base_url + "/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=" + searchString;
	    //LoadXMLString("XMLHolder", '');
     try { 
       document.getElementById('download_link').outerHTML = ''
     } catch (e) {};
	   document.getElementById('XMLHolder').innerHTML = 'Loading...';
     LoadXML("XMLHolder",str); 
     //var a = document.body.appendChild(document.createElement("a"));
     //a.download = "export.xml";
     //a.href = "data:text/xml," + document.getElementById("XMLHolder").innerHTML;
     //a.innerHTML = "[Export content]";
    })

});

(function( $ ){
    $.fn.resetElem = function() {
	$(this).prop('disabled', true).html('<option value="" selected="selected">---------</option>');
    };
})( jQuery );
