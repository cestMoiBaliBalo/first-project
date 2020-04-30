package com.xavier.computing;

import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

public class FilesCollection extends SimpleFileVisitor<Path> {
    private int count;
    private int total;
    private Pattern pattern;
    private ArrayList<String[]> files = new ArrayList<>();
    private Map<String, Integer> directories = new HashMap<>();

    public FilesCollection() {
        this.count = 0;
        this.total = 0;
        this.pattern = null;
    }

    public FilesCollection(Pattern pattern) {
        this();
        this.pattern = pattern;
    }

    public int getTotal() {
        return total;
    }

    public ArrayList<String[]> getFiles() {
        return files;
    }

    public Map<String, Integer> getDirectories() {
        return directories;
    }

    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
        String[] files = new String[3];
        String _file = file.toAbsolutePath().toString();
        String _parent = file.toAbsolutePath().getParent().toString();
        boolean included = true;
        if (this.pattern != null) {
            included = this.pattern.matcher(_file).matches();
        }
        if (included) {
            System.out.println(_file);
            files[0] = _file;
            files[1] = attrs.lastModifiedTime().toString();
            files[2] = Long.toString(attrs.size());
            this.files.add(files);
            count++;
            total++;
            this.directories.put(_parent, count);
        }
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
        if (count > 0) {
            System.out.println("--> " + count + " files.\n\n");
            count = 0;
        }
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult visitFileFailed(Path file, IOException exc) throws IOException {
        return FileVisitResult.CONTINUE;
    }
}
