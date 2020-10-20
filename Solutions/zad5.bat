@echo off

ffmpeg -i %1 -ss 00:02:10.200 -vframes 1 miniature.png