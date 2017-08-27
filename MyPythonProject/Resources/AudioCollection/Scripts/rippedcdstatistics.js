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
            var $postdata = $.get("/audiocollection/refreshrippedcd");
            $postdata.done(function() {
                $(location).attr("href", "/audiocollection/rippedcdstatistics?view=" + $("#container").find("form").children("select").children(":selected").attr("value"));
            });
        });
    };


    //     -----------------------
    //  3. Change statistics view.
    //     -----------------------
    privates.changestatisticsview = function() {
        $("#view").change(function() {
            $("form").submit();
        });
    };


    //     ----------------------
    //  4. Object initialization.
    //     ----------------------
    publics.init = function() {
        var div2,
            text,
            sections,
            newbutton;

        // -----
        $.tablesorter.addParser({
            id: "months",
            is: function() {
                return false; // return false so this parser is not auto detected.
            },
            format: function(s) {
                return $("td:contains('" + s + "')").attr("id");
            },
            type: "numeric"
        });

        // -----
        $("#table1").tablesorter({
            sortList: [
                [0, 1]
            ]
        });
        $("#table3").tablesorter({
            sortList: [
                [0, 0]
            ]
        });
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

        // ----- Insert "refresh" button.
        //       No button will be displayed if javascript/jQuery isn't available. It is a progressive enhancement.
        div2 = document.querySelector("#div2");
        // -----
        sections = div2.querySelectorAll("div");
        div2.insertBefore(document.createElement("div"), sections[0]);
        sections = div2.querySelectorAll("div");
        // -----
        newbutton = document.createElement("button");
        newbutton.className = "button";
        newbutton.type = "button";
        newbutton.id = "refresh";
        text = document.createTextNode("Refresh");
        // -----
        newbutton.appendChild(text);
        sections[0].appendChild(newbutton);

        // ----- Configure page controlers.
        privates.refresh();
        privates.changestatisticsview();

    };


})(website.rippedcdstatistics = {});
