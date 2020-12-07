package com.computing.xavier;

import picocli.CommandLine;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.Callable;
import java.util.regex.Pattern;

@CommandLine.Command()
public class Main implements Callable<Integer> {
    private enum Environment {PRODUCTION, BACKUP}

    @CommandLine.Parameters(index = "0", description = "Scanned directory. Mandatory.")
    private Path path;

    @CommandLine.Parameters(index = "1", description = "Target ID.")
    private int target;

    @CommandLine.Parameters(index = "2", description = "Environment ID.")
    private Environment environment;

    @CommandLine.Option(names = {"-r", "--regex"}, paramLabel = "REGEX", description = "Regular expression to filter files. Facultative.")
    private Pattern pattern;

    @CommandLine.Option(names = {"-o", "--output"}, paramLabel = "OUTPUT File", description = "Output file to list results. Facultative.")
    private Path output;

    public static void main(String[] args) {
        int exitCode = new CommandLine(new Main()).execute(args);
        System.exit(exitCode);
    }

    @Override
    public Integer call() throws Exception {
        if (Files.exists(path)) {

            FilesCollection collection;
            try {
                collection = new FilesCollection(pattern);
            } catch (NullPointerException exception) {
                collection = new FilesCollection();
            }

            try {
                Files.walkFileTree(path, collection);
            } catch (IOException exception) {
                System.out.println(exception.getMessage());
            }

            int total = collection.getTotal();
            if (total > 0) {
                System.out.println("--> " + total + " total files.\n\n");

                try {
                    writeFile(Integer.toString(target), environment.toString(), output, collection.getFiles());
                } catch (IOException exception) {
                    System.out.println(exception.getMessage());
                } catch (NullPointerException ignore) {
                }

                Map<String, Integer> directories = collection.getDirectories();
                Map<String, Integer> sorted = new TreeMap<>(directories);
                for (String key : sorted.keySet()) {
                    System.out.println("" + key + ": " + directories.get(key) + " files.");
                }

            }

        }
        return 0;
    }

    private static void writeFile(String target, String environment, Path path, List<String[]> files) throws IOException {
        try (BufferedWriter outfile = Files.newBufferedWriter(path, StandardCharsets.ISO_8859_1, StandardOpenOption.CREATE, StandardOpenOption.WRITE, StandardOpenOption.APPEND)) {
            for (String[] file : files) {
                outfile.write(target + "|" + environment + "|" + file[0] + "|" + file[1] + "|" + file[2]);
                outfile.newLine();
            }
        }
    }

}
