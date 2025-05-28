pkgname=pymprisence
pkgver=1.1.0
pkgrel=1
arch=('x86_64')
license=('MIT')
depends=('python3')
source=()

build() {
    mkdir -p "$startdir/build"
    cd "$startdir/build"
    pyinstaller --clean "$startdir/linux.spec"
}

package() {
    cd "$startdir"
    install -Dm755 "build/dist/pymprisence" "$pkgdir/usr/local/bin/pymprisence"
    install -Dm644 "systemd/pymprisence.service" "$pkgdir/usr/lib/systemd/user/pymprisence.service"
}