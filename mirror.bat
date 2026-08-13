@echo off
setlocal enabledelayedexpansion

rem ---------------------------------------------------------------------------
rem  mirror.bat - the backup of record for BOTH repos, and an observable one.
rem  Run from Corpus (RENDER's final step); it backs up OSINT and CORPUS together.
rem
rem  Per repo, two legs to Dropbox:
rem    robocopy  <repo> -> Dropbox\<name>-mirror   (working tree, no .git)
rem    git bundle --all -> Dropbox\<name>-mirror   (whole history, one file)
rem  Then ONE FreeFileSync leg for both:
rem    repos-to-flash.ffs_batch -> D:\   (a straight file copy of both repos AND
rem    Bill's Dropbox\Github, working tree incl. .git, to the D: flash drive; NOT the mirrors)
rem
rem  OSINT is READ ONLY from here: these legs read it and write the backup
rem  elsewhere - nothing is ever written back into OSINT. budget-archive is a
rem  junction in OSINT; /XJ stops robocopy following it into a second Dropbox copy.
rem  CORPUS's .workroot is transient symlinks into OSINT (/XD keeps it out).
rem
rem  robocopy returns a BIT FIELD: 0-7 are all success, only >=8 is a real
rem  failure - so test `GEQ 8`, not `errorlevel 1`. One dated line goes to
rem  logs\mirror_log.md with every exit code. ASCII only (cmd reads .bat in the
rem  OEM codepage, so a UTF-8 em-dash would reach the log as mojibake).
rem
rem  Exit code: 0 if every leg passed, 1 otherwise.
rem ---------------------------------------------------------------------------

set "OSINT=C:\OSINT"
set "OSINT_DBX=C:\Users\bill\Dropbox\OSINT-mirror"
set "CORPUS=C:\CORPUS"
set "CORPUS_DBX=C:\Users\bill\Dropbox\Corpus-mirror"
set "LOG=%CORPUS%\logs\mirror_log.md"
set "STATUS=ok"

for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyy-MM-dd HH:mm')"') do set "TS=%%t"

rem === OSINT: working tree + history to Dropbox (read only on OSINT) ===========
robocopy "%OSINT%" "%OSINT_DBX%" /MIR /XD .git budget-archive /XJ /NFL /NDL /NP
set "ORC=!ERRORLEVEL!"
if !ORC! GEQ 8 set "STATUS=FAIL"
git -C "%OSINT%" bundle create "%OSINT_DBX%\osint.bundle" --all
set "OGB=!ERRORLEVEL!"
if not "!OGB!"=="0" set "STATUS=FAIL"

rem === CORPUS: working tree + history to Dropbox ==============================
robocopy "%CORPUS%" "%CORPUS_DBX%" /MIR /XD .git .workroot /XJ /NFL /NDL /NP
set "CRC=!ERRORLEVEL!"
if !CRC! GEQ 8 set "STATUS=FAIL"
git -C "%CORPUS%" bundle create "%CORPUS_DBX%\corpus.bundle" --all
set "CGB=!ERRORLEVEL!"
if not "!CGB!"=="0" set "STATUS=FAIL"

rem === leg 3: FreeFileSync straight-copies both repos to the D: flash drive ====
rem  repos-to-flash.ffs_batch copies both repos (working tree incl. .git) and
rem  Bill's Dropbox\Github straight to D: - three pairs. It does NOT touch the
rem  Dropbox mirrors above. Keep
rem  Errors Ignore="false" so a genuine error reaches us; FFS returns 0 = success,
rem  non-zero = warnings, errors or cancellation.
"C:\Program Files\FreeFileSync\FreeFileSync.exe" "%~dp0repos-to-flash.ffs_batch"
set "FF=!ERRORLEVEL!"
if not "!FF!"=="0" set "STATUS=FAIL"

rem --- one dated line, whatever happened --------------------------------------
if not exist "%CORPUS%\logs" mkdir "%CORPUS%\logs"
>>"%LOG%" echo - **!TS!** - !STATUS! - osint(robocopy=!ORC! bundle=!OGB!) corpus(robocopy=!CRC! bundle=!CGB!) ffs=!FF!

if "!STATUS!"=="FAIL" (
  echo.
  echo mirror.bat: FAILED - osint(robocopy=!ORC! bundle=!OGB!) corpus(robocopy=!CRC! bundle=!CGB!) ffs=!FF!
  echo   see %LOG% and the FreeFileSync log
  endlocal & exit /b 1
)

echo mirror.bat: ok - osint(robocopy=!ORC! bundle=!OGB!) corpus(robocopy=!CRC! bundle=!CGB!) ffs=!FF!
endlocal & exit /b 0
