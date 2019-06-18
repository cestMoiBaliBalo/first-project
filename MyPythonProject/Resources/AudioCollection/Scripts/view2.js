"use strict";
var root = root || "/audiocollection/";
var website = website || {};


(function (publics) {

    function append_button(parent, element, text) {
        // """
        // Private function to append a button using standard JS syntax.
        // """
        var button = document.createElement("button");
        var textButton = document.createTextNode(text.capitalize());
        button.className = "button";
        button.type = "button";
        button.id = text;
        button.appendChild(textButton);
        parent.insertBefore(button, element);
    }

    function append_anotherbutton(element, text) {
        // """
        // Private function to append a button using jQuery syntax.
        // How use me: append_anotherbutton($(".button:eq(0)"), "button text");
        // """
        var button = document.createElement("button");
        var textButton = document.createTextNode(text);
        button.className = "button";
        button.type = "button";
        button.id = text;
        button.appendChild(textButton);
        $(button.outerHTML).insertBefore(element);
    }

    function views(element) {
        // """
        // Ripped discs viewed by artists, genres, ripped months or ripped years.
        // One private single function to handle four click events.
        // """
        var mapping = {"artists": "/audiocollection/rippeddiscsviewbyartist",
                       "genres": "/audiocollection/rippeddiscsviewbygenre",
                       "months": "/audiocollection/rippeddiscsviewbymonth",
                       "years": "/audiocollection/rippeddiscsviewbyyear"};
        $("#" + element).click(function() {
            $(location).attr("href", mapping[element]);
        });
    }

    publics.initialize = function() {

        // -----
        var anchor,
            anchorText,
            key,
            browser;
        var paths = window.location.pathname.split("/");
        var pathname = paths[paths.length - 1];
        var search = window.location.search;
        if (search !== "") {
            browser = document.querySelector("div.browser");
            anchor = document.createElement("a");
            anchorText = document.createTextNode("All");
            anchor.href = root + pathname;
            key = search.split("=")[0];
            switch (key) {
                case "?artistsort":
                    anchor.title = "afficher tous les artistes";
                    break;
                case "?genre":
                    anchor.title = "afficher tous les genres";
                    break;
                case "?month":
                    anchor.title = "afficher tous les mois";
                    break;
                case "?year":
                    anchor.title = "afficher toutes les années";
            }
            anchor.appendChild(anchorText);
            browser.insertBefore(anchor, document.querySelector("div.browser > a"));
        }

        // -----
        var buttons = [];
        var i,
            len;
        var view = $("div#wrapper").attr("class");
        switch (view) {
            case "artists":
                buttons = ["genres", "months", "years"];
                break;
            case "genres":
                buttons = ["artists", "months", "years"];
                break;
            case "months":
                buttons = ["artists", "genres", "years"];
                break;
            case "years":
                buttons = ["artists", "genres", "months"];
        }
        if (buttons) {
            for (i = 0, len = 3; i < len; i++) {
                append_button(document.querySelector("div#div2").firstElementChild, document.querySelector("#refresh"), buttons[i]);
            }
        }

    };

    publics.browse = function() {
        var month;

        $("div.browser > a").hover(function() {
            $("div.browser > a").each(function() {
                if ($(this).hasClass("bold")) {
                    month = $(this).text();
                }
            });
            $("div.browser > a").removeClass().addClass("hover");
            $(this).removeClass().addClass("bold");
        },
        function() {
            $("div.browser > a").removeClass();
            $("div.browser > a").filter(function() {
                return $(this).text() === month;
            }).addClass("bold");
        });

    };

    publics.views = function() {
        views("artists");
        views("genres");
        views("months");
        views("years");
    };

    publics.init = function() {
        website.view2.initialize();
        website.view2.browse();
        website.view2.views();
    };



})(website.view2 = {});
