"use strict";
var website = website || {};


(function(publics) {


    //     --------------------
    //  1. Set inner variables.
    //     --------------------
    var privates = {};


    //     -------------
    //  2. Refresh page.
    //     -------------
    privates.refresh = function() {
        $("#refresh").on("click", function() {
            var $postdata = $.get("/audiocollection/refreshdigitalalbums");
            $postdata.done(function() {
                $(location).attr("href", "/audiocollection/digitalalbums_playedstatistics");
            });
        });
    };


    //     ----------------------
    //  4. Object initialization.
    //     ----------------------
    publics.init = function() {

        // -----
        $.tablesorter.addParser({
            id: "timestamps",
            is: function(s) {
                return false; // return false so this parser is not auto detected.
            },
            format: function(s) {
                return $("td:contains('" + s + "')").attr("id").split("-")[1];
            },
            type: "numeric"
        });

        $.tablesorter.addParser({
            id: "artists",
            is: function(s) {
                return false; // return false so this parser is not auto detected.
            },
            format: function(s) {
                return $("td:contains('" + s + "')").attr("id");
            },
            type: "text"
        });

        $(function() {
            $("#table2").tablesorter({
                headers: {
                    0: {
                        sorter: "months"
                    }
                },
                sortList: [
                    [0, 1]
                ]
            });
        });

        $(function() {
            $("#table5").tablesorter({
                headers: {
                    1: {
                        sorter: "artists"
                    },
                    2: {
                        sorter: false
                    },
                    3: {
                        sorter: false
                    },
                    5: {
                        sorter: "timestamps"
                    }
                },
                sortList: [
                    [4, 1],
                    [1, 0],
                    [0, 0]
                ]
            });
        });

        // ----- Insert "refresh" button.
        //       No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        var div1 = document.querySelector("#div1");
        // -----
        var text = document.createTextNode("Refresh");
        var button = document.createElement("button");
        var div2 = document.createElement("div");
        // -----
        button.type = "button";
        button.id = "refresh";
        button.className = "button";
        div2.id = "div2";
        // -----
        button.appendChild(text);
        div2.appendChild(button);
        div1.parentNode.appendChild(div2);

        // ----- Configure page controlers.
        privates.refresh();

    };


})(website.digitalalbumsstatistics = {});