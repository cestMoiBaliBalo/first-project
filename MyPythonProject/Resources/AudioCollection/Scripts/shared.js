"use strict";
var root = root || "/audiocollection/";
var website = website || {};


(function(publics) {


    //     -------------
    //  1. Set mappings.
    //     -------------
    var mapping = {"/audiocollection/digitalalbumsview": "refreshdigitalalbums",
                   "/audiocollection/rippeddiscsview": "refreshrippeddiscs",
                   "/audiocollection/playeddiscsview": "refreshplayeddiscs",
                   "/audiocollection/rippeddiscsviewbyartist": "rippeddiscsviewbyartist",
                   "/audiocollection/rippeddiscsviewbygenre": "rippeddiscsviewbygenre",
                   "/audiocollection/rippeddiscsviewbymonth": "rippeddiscsviewbymonth",
                   "/audiocollection/rippeddiscsviewbyyear": "rippeddiscsviewbyyear"};


    //     ----------------------------------------
    //  1. initialize_page page with additional buttons.
    //     ----------------------------------------
    publics.initialize_page = function() {
        var buttons,
            div,
            refresh,
            shutdown,
            text;

        //  3.1. Insert additional buttons.
        div = document.querySelector("#div2");
        buttons = document.createElement("div");

        //  3.1.a. Insert "refresh" button.
        //         No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        refresh = document.createElement("button");
        text = document.createTextNode("Refresh");
        refresh.className = "button";
        refresh.type = "button";
        refresh.id = "refresh";
        refresh.appendChild(text);
        buttons.appendChild(refresh);

        //  3.1.b. Insert "shutdown" button.
        //         No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        shutdown = document.createElement("button");
        text = document.createTextNode("Shutdown");
        shutdown.className = "button";
        shutdown.type = "button";
        shutdown.id = "shutdown";
        shutdown.appendChild(text);
        buttons.appendChild(shutdown);

        // -----
        div.appendChild(buttons);

    };


    //     ---------------------
    //  3. Refresh current page.
    //     ---------------------
    publics.refresh_page = function() {
        $("#refresh").click(function() {
            var $pathname = location.pathname,
                $postdata = $.get(root + mapping[$pathname]);
            $postdata.done(function() {
                $(location).attr("href", $pathname);
            });
        });
    };


    //     --------------
    //  4. Shutdown site.
    //     --------------
    publics.shutdown = function() {
        $("#shutdown").click(function() {
            $(location).attr("href", root + "shutdown");
        });
    };


    //     ----------------
    //  5. Pages controler.
    //     ----------------
    publics.load = function() {
        website.initialize_page();
        website.refresh_page();
        website.shutdown();
    };


})(website);


$(function() {
    var $specific = $("body").attr("id");

    // --> Run common script.
    website.load();

    // --> Run page specific script.
    if (website[$specific] !== undefined) {
        website[$specific].load();
    }

});
