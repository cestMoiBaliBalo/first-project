package com.computing.xavier;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class getAlbumTypeTest {

    @Test
    void getType01() {
        getAlbumType type = new getAlbumType("F:\\S\\Springsteen, Bruce\\1\\2020 - Letter To You");
        assertEquals(type.getType(), 1);
    }

    @Test
    void getType02() {
        getAlbumType type = new getAlbumType("F:\\S\\Springsteen, Bruce\\2\\1980");
        assertEquals(type.getType(), 2);
    }

    @Test
    void getType03() {
        getAlbumType type = new getAlbumType("F:\\S\\Springsteen, Bruce\\2");
        assertEquals(type.getType(), 2);
    }

    @Test
    void getType04() {
        getAlbumType type = new getAlbumType("F:\\S\\Springsteen, Bruce");
        assertEquals(type.getType(), 400);
    }

    @Test
    void getType05() {
        getAlbumType type = new getAlbumType("F:\\S");
        assertEquals(type.getType(), 400);
    }

    @Test
    void getType06a() {
        getAlbumType type = new getAlbumType("G:\\Computing\\Java");
        assertEquals(type.getType(), 300);
    }

    @Test
    void getType06b() {
        getAlbumType type = new getAlbumType("G:\\Computing");
        assertEquals(type.getType(), 300);
    }

    @Test
    void getType07() {
        getAlbumType type = new getAlbumType("F:\\M\\Metric");
        assertEquals(type.getType(), 400);
    }

    @Test
    void getType08() {
        getAlbumType type = new getAlbumType("F:\\M\\Metric\\2018 - Art of Doubt");
        assertEquals(type.getType(), 1);
    }

    @Test
    void getType09() {
        getAlbumType type = new getAlbumType("F:\\M\\Metric\\2018 - Art of Doubt\\1.Free Lossless Audio Codec");
        assertEquals(type.getType(), 1);
    }

    @Test
    void getType10() {
        getAlbumType type = new getAlbumType("F:\\P\\Pink Floyd\\1988 - Delicate Sound of Thunder\\CD1");
        assertEquals(type.getType(), 1);
    }

    @Test
    void getType11() {
        getAlbumType type = new getAlbumType("F:\\P\\Pink Floyd\\1988 - Delicate Sound of Thunder\\CD1\\1.Free Lossless Audio Codec");
        assertEquals(type.getType(), 1);
    }

    @Test
    void getType12() {
        getAlbumType type = new getAlbumType("F:\\P\\Pink Floyd\\2020 - Delicate Sound of Thunder\\CD1\\1.Free Lossless Audio Codec");
        assertEquals(type.getType(), 200);
    }

    @Test
    void getType13() {
        getAlbumType type = new getAlbumType("F:\\P\\Pink Floyd\\1988 - Delicate Sound of Thunder\\1.Free Lossless Audio Codec");
        assertEquals(type.getType(), 200);
    }

}