import filecmp
import os
import sys
import unittest
import warnings
from pathlib import Path, PurePath  # nueva forma de trabajar con rutas

# Confirmamos que tenemos en el path la ruta de la aplicacion, para poder lanzarlo desde cualquier ruta
absolut_path: PurePath = PurePath(os.path.realpath(__file__))  # Ruta absoluta del fichero
new_path: str = f'{absolut_path.parent}/../../'
if new_path not in sys.path:
    sys.path.append(new_path)

from app.models.model_t_grantorrent import GranTorrent
from app.models.model_t_showrss import ShowRss


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if not sys.warnoptions:
            warnings.simplefilter("ignore")
        # print(self._testMethodName)

        path_torrent: Path = Path('./torrents/')

        # GranTorrent
        cls.torrent_grantorrent: Path = Path(path_torrent, 'Person_Of_Interest_Temp3_720p_original.torrent')
        url: str = 'https://grantorrent.tv/series-2/person-of-interest-temporada-3/'
        cls.grantorrent: GranTorrent = GranTorrent('nombre', url, path_torrent)
        cls.correct_grantorrent: bool = cls.grantorrent.download_file_torrent()

        cls.expect_grantorrent: GranTorrent = GranTorrent('Person_Of_Interest_Temp3_720p', url, path_torrent)
        cls.expect_grantorrent.url_torrent = 'https://files.grantorrent.tv/torrents/series/Person_Of_Interest_Temp3_720p.torrent'

        # ShowRss
        cls.torrent_showrss: Path = Path(path_torrent, 'Mr.Robot.S04E05.1080p.WEB.x264-XLF[rarbg]_original.torrent')
        magnet = "magnet:?xt=urn:btih:834DAC50F4F3C8F167C72EDF913FA9E36CF79AF5&dn=Mr+Robot+S04E05+1080p+WEB+x264+XLF&tr=" \
                 "udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%" \
                 "3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2F" \
                 "tracker.trackerfix.com%3A80%2Fannounce"
        cls.showrss: ShowRss = ShowRss('Mr.Robot.S04E05.1080p.WEB.x264-XLF[rarbg]', magnet, path_torrent)
        cls.correct_showrss: bool = cls.showrss.download_file_torrent()
        cls.expect_showrss: ShowRss = ShowRss('Mr.Robot.S04E05.1080p.WEB.x264-XLF[rarbg]', magnet, path_torrent)
        cls.expect_showrss.url_web = magnet
        # cls.expect_showrss.path_file_torrent = cls.torrent_showrss

    def test_grantorrent_class(self):
        """
        Comprueba que la informacion de la clase se obtiene correctamente
        :return:
        """
        self.assertTrue(self.grantorrent.__eq__(self.expect_grantorrent))
        # self.assertEqual(True, True)

    def test_grantorrent_download(self):
        """
        Comprueba que se ha descargado correctamente el fichero torrent
        :return:
        """
        self.assertTrue(self.correct_grantorrent)

    def test_grantorrent_files(self):
        """
        Comprueba que el fichero torrent descargado es correcto
        :return:
        """
        self.assertTrue(filecmp.cmp(self.grantorrent.path_file_torrent, self.torrent_grantorrent))
        # self.assertEqual(True, True)

    def test_showrss_class(self):
        """
        Comprueba que la informacion de la clase se obtiene correctamente
        :return:
        """
        self.assertTrue(self.showrss.__eq__(self.expect_showrss))
        # self.assertEqual(True, True)

    def test_showrss_download(self):
        """
        Comprueba que se ha descargado correctamente el fichero torrent
        :return:
        """
        self.assertTrue(self.correct_showrss)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Borramos los torrents descargados
        :return:
        """
        if cls.grantorrent.path_file_torrent.exists():
            Path.unlink(cls.grantorrent.path_file_torrent)

        if cls.showrss.path_file_torrent.exists():
            Path.unlink(cls.showrss.path_file_torrent)


if __name__ == '__main__':
    unittest.main(verbosity=2)
