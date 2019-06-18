"use strict";


if (!Number.prototype.numberToText) {
    Number.prototype.numberToText = function() {
        return this + "";
    };
}


if (!String.prototype.lPadding) {
    String.prototype.lPadding = function(len, char) {
        var length,
            lpad = "";

        if (!char) {
            char = " ";
        }
        length = len - this.length;
        if (length < 0) {
            return this;
        }
        if (!length) {
            return this;
        }
        for (var i = 0; i < length; i++) {
            lpad += char;
        }
        return lpad + this;

    };
}


if (!String.prototype.trim) {
    String.prototype.trim = function() {
        return this.replace(/^\w*(.+)\w*$/, "$1");
    };
}


if (!String.prototype.capitalize) {
    String.prototype.capitalize = function() {
      var word = this.toLowerCase();
      return word.charAt(0).toUpperCase() + word.slice(1);
    };
}
