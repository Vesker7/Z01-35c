@echo off
set _ffmpeg="C:\ffmpeg.exe"

%_ffmpeg% -i %1 -ss 00:02:10.200 -vframes 1 miniature.png 2>&1
