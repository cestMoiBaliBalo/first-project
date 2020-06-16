package com.computing.xavier;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.regex.Pattern;

public class Main {

    public static void main(String[] args) {
        Pattern pattern;

        // Is input path coherent?
        Path path = Paths.get(args[0]);
        if (!path.isAbsolute()){
            System.exit(100);
        }
        if (!Files.exists(path)) {
            System.exit(200);
        }

        // Bootleg album.
        pattern = Pattern.compile("^([^\\\\]+\\\\){2}([^\\\\]+)\\\\\\b2\\b(\\\\)?.*$");
        if (pattern.matcher(args[0]).matches()) {
            System.exit(2);
        }

        // Default album.
        pattern = Pattern.compile("^([^\\\\]+\\\\){2}([^\\\\]+)\\\\\\b1\\b(\\\\)?.*$");
        if (pattern.matcher(args[0]).matches()) {
            System.exit(1);
        }
        pattern = Pattern.compile("^(?>((?>[^\\\\]+)\\\\){4})(CD\\d\\\\)?.+$");
        if (pattern.matcher(args[0]).matches()) {
            System.exit(1);
        }

        System.exit(0);
    }
}
