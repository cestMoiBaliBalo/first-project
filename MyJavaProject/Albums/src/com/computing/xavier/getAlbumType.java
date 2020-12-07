package com.computing.xavier;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Pattern;

public class getAlbumType {
    private final String path;

    public getAlbumType(String path) {
        this.path = path;
    }

    public int getType() {

        Pattern pattern;

        // Is input path coherent?
        // Input path must be composed of a root drive and must exist into the file system.
        Path path = Path.of(this.path);
        if (!path.isAbsolute()) {
            return 100;
        }
        if (!Files.exists(path)) {
            return 200;
        }

        // Root drive must be the Audio drive.
        pattern = Pattern.compile("^(?!F:\\\\).+$");
        if (pattern.matcher(this.path).matches()) {
            return 300;
        }

        // Four directories must be at least provided.
        pattern = Pattern.compile("^([^\\\\]+\\\\){3}[^\\\\]+(\\\\.+)?$");
        if (!pattern.matcher(this.path).matches()) {
            return 400;
        }

        // A bootleg album is assumed if the fourth directory of the directories tree is the number "2".
        pattern = Pattern.compile("^([^\\\\]+\\\\){3}\\b2\\b(\\\\)?.*$");
        if (pattern.matcher(this.path).matches()) {
            return 2;
        }

        // A default album is assumed by default.
        return 1;

    }

}
