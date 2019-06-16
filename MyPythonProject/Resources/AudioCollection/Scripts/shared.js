"use strict";
var root = root || "/audiocollection/";
var website = website || {};


(function(publics) {


    //     -------------
    //  1. Set mappings.
    //     -------------
    var mapping = {"/audiocollection/digitalalbumsview": "refreshdigitalalbums",
                   "/audiocollection/rippeddiscsview": "refreshrippeddiscs",
                   "/audiocollection/rippeddiscsviewbyartist": "rippeddiscsviewbyartist",
                   "/audiocollection/rippeddiscsviewbygenre": "rippeddiscsviewbygenre",
                   "/audiocollection/rippeddiscsviewbymonth": "rippeddiscsviewbymonth",
                   "/audiocollection/rippeddiscsviewbyyear": "rippeddiscsviewbyyear"};


    //     ----------------------------------------
    //  1. Initialize page with additional buttons.
    //     ----------------------------------------
    publics.initialize = function() {
        var div_buttons,
            refresh,
            shutdown,
            div2,
            form,
            text;

        //  3.1. Insert additional buttons.
        div2 = document.querySelector("#div2");
        form = document.querySelector("#form");
        div_buttons = document.createElement("div");

        //  3.1.a. Insert "refresh" button.
        //         No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        refresh = document.createElement("button");
        text = document.createTextNode("Refresh");
        refresh.className = "button";
        refresh.type = "button";
        refresh.id = "refresh";
        refresh.appendChild(text);
        div_buttons.appendChild(refresh);

        //  3.1.b. Insert "shutdown" button.
        //         No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        shutdown = document.createElement("button");
        text = document.createTextNode("Shutdown");
        shutdown.className = "button";
        shutdown.type = "button";
        shutdown.id = "shutdown";
        shutdown.appendChild(text);
        div_buttons.appendChild(shutdown);

        // -----
        div2.insertBefore(div_buttons, form.parentNode);

    };


    //     ------------
    //  2. Browse site.
    //     ------------
    publics.browse = function() {
        $("li.dropdown:first > a:first").click(function() {
            $(location).attr("href", root + "rippeddiscsview");
        });
    };


    //     ---------------------
    //  3. Refresh current page.
    //     ---------------------
    publics.refresh = function() {
        var pathname;
        pathname = window.location.pathname;
        $("#refresh").click(function() {
            var $postdata = $.get(root + mapping[pathname]);
            $postdata.done(function() {
                $(location).attr("href", pathname);
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
    publics.init = function() {
        website.initialize();
        website.browse();
        website.refresh();
        website.shutdown();
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
