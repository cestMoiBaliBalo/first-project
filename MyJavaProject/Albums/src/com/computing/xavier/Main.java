package com.computing.xavier;


public class Main {

    public static void main(String[] args) {
        getAlbumType type = new getAlbumType(args[0]);
        System.exit(type.getType());
    }

}
