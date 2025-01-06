{pkgs}: {
  deps = [
    pkgs.nettools
    pkgs.uwsgi
    pkgs.parallel-full
    pkgs.percona-server
    pkgs.cacert
    pkgs.zlib
    pkgs.xcodebuild
    pkgs.glibcLocales
    pkgs.libmysqlclient
    pkgs.flite
    pkgs.pgadmin4
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
  ];
}
