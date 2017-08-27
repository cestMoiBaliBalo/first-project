"use strict";
var website = website || {};


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var privates = {};


    //     --------------
    //  2. Pages browser.
    //     --------------
    privates.browse = function() {
        $("li.dropdown:first > a:first").on("click", function() {
            $(this).attr("href", "/audiocollection/rippedcdview");
        });
        $("li.dropdown:first > div.dropdown-content > div.sub-dropdown > a").on("click", function() {
            $(this).attr("href", "/audiocollection/rippedcdviewbyyear?year=" + $(this).text());
        });
    };


    //     ----------------
    //  3. Pages controler.
    //     ----------------
    publics.init = function() {
        privates.browse();
    };


})(website);


$(function() {
    var $specific = $("body").attr("id");

    // --> Run common script.
    website.init();

    // --> Run page specific script.
    if (website[$specific] !== undefined) {
        website[$specific].init();
    }

});
