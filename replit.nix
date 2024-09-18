{pkgs}: {
  deps = [
    pkgs.mailutils
    pkgs.lsof
    pkgs.glibcLocales
    pkgs.postgresql
  ];
}
