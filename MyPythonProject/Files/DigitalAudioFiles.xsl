<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="utf-8" indent="yes"/>


    <!--  A. Main structure. -->
    <xsl:template match="Files">
        <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
        <html>
            <head>
                <link rel="stylesheet">
                    <xsl:attribute name="href">
                        <xsl:value-of select="./@css"/>
                    </xsl:attribute>
                </link>
                <title><xsl:value-of select="./@title"/></title>
            </head>
            <body>
                <p style="float: left;">
                  <a href="http://jigsaw.w3.org/css-validator/check/referer">
                      <img style="border:0;width:88px;height:31px"
                          src="http://jigsaw.w3.org/css-validator/images/vcss"
                          alt="Valid CSS!" />
                  </a>
                </p>
                <h1>digital audio files</h1>
                <xsl:apply-templates select="Updated"/>
                <h2>Files</h2>
                <table class="files">
                    <tr>
                        <th class="left1">File</th>
                        <th class="left2">Date</th>
                        <th class="center">Seconds</th>
                    </tr>
                    <xsl:apply-templates select="FilesList/File"/>
                </table>
                <h2>Recent files</h2>
                <table class="files">
                    <tr>
                        <th class="left1">File</th>
                        <th class="left2">Date</th>
                        <th class="center">Seconds</th>
                    </tr>
                    <xsl:apply-templates select="RecentFilesList/File"/>
                </table>
                <h2>Files by artist</h2>
                <xsl:apply-templates select="FilesByArtist/Artist" mode="files"/>
                <table>
                    <tr>
                        <th>Extension</th>
                        <th>Count</th>
                    </tr>
                     <xsl:apply-templates select="ExtensionsList/Extension" mode="extensions"/>
                </table>
                <xsl:apply-templates select="ArtistsList/Artist"/>
            </body>
        </html>
    </xsl:template>


    <!--  B. Templates. -->

    <!--  B.1. Last update date. -->
    <xsl:template match="Updated">
        <p><xsl:value-of select="."/></p>
    </xsl:template>

    <!--  B.2. Scanned directory. -->
    <xsl:template match="Directory">
        <p class="floatleft">Directory: <xsl:value-of select="."/></p>
    </xsl:template>

    <!--  B.3. Both whole files and recent files list. -->
    <xsl:template match="File">
        <tr>
            <td><xsl:value-of select="."/></td>
            <td><xsl:value-of select="./@converted"/></td>
            <td class="seconds"><xsl:value-of select="./@seconds"/></td>
        </tr>
    </xsl:template>

    <!--  B.4. Files by artist list. -->
    <xsl:template match="Artist" mode="files">
        <h3><xsl:value-of select="./@name"/></h3>
        <p><xsl:value-of select="./@count"/></p>
        <table class="files">
            <tr>
                <th class="left1">File</th>
                <th class="left2">Date</th>
                <th class="center">Seconds</th>
            </tr>
            <xsl:apply-templates select="File"/>
        </table>
    </xsl:template>

    <!--  B.5. Extensions list. -->
    <xsl:template match="Extension" mode="extensions">
        <tr>
            <td><xsl:value-of select="./@name"/></td>
            <td><xsl:value-of select="."/></td>
        </tr>
    </xsl:template>

    <!--  B.6. Artists list with extensions detail. -->

    <!--  B.6.a. Header. -->
    <xsl:template match="Artist">
        <h3><xsl:value-of select="./@name"/></h3>
        <p><xsl:value-of select="./@count"/></p>
        <table>
            <tr>
                <th>Extension</th>
                <th>Count</th>
            </tr>
            <xsl:apply-templates select="Extension" mode="artists"/>
        </table>
    </xsl:template>

    <!--  B.6.b. Detail. -->
    <xsl:template match="Extension" mode="artists">
        <tr>
            <td><xsl:value-of select="./@name"/></td>
            <td><xsl:value-of select="."/></td>
        </tr>
    </xsl:template>


</xsl:stylesheet>
