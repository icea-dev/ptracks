#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
dlg_trajetoria

mantém as informações sobre a dialog de trajetória

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.2  2015/nov  mlabru
pep8 style conventions

revision 0.1  2014/nov  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.2$"
__author__ = "mlabru, sophosoft"
__date__ = "2015/12"

# < imports >--------------------------------------------------------------------------------------

# python library
import json
import os

# PyQt library
from PyQt4 import QtCore
from PyQt4 import QtGui

# view
from . import dlg_trajetoria_ui as dlg

# < class CDlgTrajetoria >-------------------------------------------------------------------------

class CDlgTrajetoria(QtGui.QDialog, dlg.Ui_CDlgTrajetoria):
    """
    mantém as informações sobre a dialog de trajetória
    """
    # ---------------------------------------------------------------------------------------------

    def __init__(self, fsck_http, fdct_config, f_strip_cur, fdct_trj, f_parent=None):
        """
        @param fsck_http: socket de comunicação com o servidor
        @param fdct_config: dicionário de configuração
        @param f_strip_cur: strip selecionada
        @param fdct_trj: dicionário de trajetórias
        @param f_parent: janela pai
        """
        # init super class
        super(CDlgTrajetoria, self).__init__(f_parent)

        # salva o control manager localmente
        # self.__control = f_control

        # salva o socket de comunicação
        self.__sck_http = fsck_http
        assert self.__sck_http

        # salva o dicionário de configuração
        self.__dct_config = fdct_config
        assert self.__dct_config is not None

        # carrega o dicionário
        self.__dct_trj = self.__load_trj(fdct_trj)
        assert self.__dct_trj is not None

        # monta a dialog
        self.setupUi(self)

        # configura título da dialog
        self.setWindowTitle(u"Procedimento de Trajetória")

        # configurações de conexões slot/signal
        self.__config_connects()

        # configurações de títulos e mensagens da janela de edição
        self.__config_texts()

        # restaura as configurações da janela de edição
        self.__restore_settings()

        # carrega as trajetórias na comboBox
        self.cbx_trj.addItems(sorted(self.__dct_trj.values()))

        # configura botões
        self.bbx_trajetoria.button(QtGui.QDialogButtonBox.Cancel).setText("&Cancela")
        self.bbx_trajetoria.button(QtGui.QDialogButtonBox.Ok).setFocus()

        # inicia os parâmetros da trajetória
        self.__update_command()

    # ---------------------------------------------------------------------------------------------
    def __config_connects(self):
        """
        configura as conexões slot/signal
        """
        # conecta spinBox
        self.cbx_trj.currentIndexChanged.connect(self.__on_cbx_currentIndexChanged)

        # conecta botão Ok da edição de trajetoria
        # self.bbx_trajetoria.accepted.connect(self.__accept)

        # conecta botão Cancela da edição de trajetoria
        # self.bbx_trajetoria.rejected.connect(self.__reject)

    # ---------------------------------------------------------------------------------------------
    def __config_texts(self):
        """
        DOCUMENT ME!
        """
        # configura títulos e mensagens
        self.__txt_settings = "CDlgTrajetoria"

    # ---------------------------------------------------------------------------------------------
    def get_data(self):
        """
        DOCUMENT ME!
        """
        # return command line
        return self.lbl_comando.text()

    # ---------------------------------------------------------------------------------------------
    def __load_trj(self, fdct_trj):
        """
        carrega o dicionário de trajetórias
        """
        # check input
        # assert f_strip_cur

        # check for requirements
        assert self.__sck_http is not None
        assert self.__dct_config is not None

        # resposta
        ldct_ans = {}

        # dicionário vazio ?
        if not fdct_trj:
            # monta o request das trajetórias
            ls_req = "data/trj.json"
            # dbg.M_DBG.debug("__load_trj:ls_req:[{}]".format(ls_req))

            # get server address
            l_srv = self.__dct_config.get("srv.addr", None)

            if l_srv is not None:
                # obtém os dados de trajetórias do servidor
                l_data = self.__sck_http.get_data(l_srv, ls_req)
                # dbg.M_DBG.debug("__load_trj:l_data:[{}]".format(l_data))

                if l_data is not None:
                    # salva a trajetórias no dicionário
                    ldct_ans = json.loads(l_data)
                    # dbg.M_DBG.debug("__load_trj:dct_trj:[{}]".format(ldct_ans))

                # senão, não achou no servidor...
                else:
                    # logger
                    l_log = logging.getLogger("CDlgTrajetoria::__load_trj")
                    l_log.setLevel(logging.ERROR)
                    l_log.error(u"<E01: tabela de trajetórias não existe no servidor.")

            # senão, não achou endereço do servidor
            else:
                # logger
                l_log = logging.getLogger("CDlgTrajetoria::__load_trj")
                l_log.setLevel(logging.WARNING)
                l_log.warning(u"<E02: srv.addr não existe na configuração.")

        # senão,...
        else:
            # para todas as trajetórias...
            for l_trj in fdct_trj.values():
                # coloca na resposta
                ldct_ans[l_trj.i_prc_id] = l_trj.s_prc_desc

        # return
        return ldct_ans

    # ---------------------------------------------------------------------------------------------
    def __restore_settings(self):
        """
        restaura as configurações salvas para esta janela
        """
        # obtém os settings
        l_set = QtCore.QSettings("sophosoft", "piloto")
        assert l_set

        # restaura geometria da janela
        self.restoreGeometry(l_set.value("%s/Geometry" % (self.__txt_settings)).toByteArray())

    # ---------------------------------------------------------------------------------------------
    def __update_command(self):
        """
        DOCUMENT ME!
        """
        # para todas as trajetórias...
        for l_key, l_trj in self.__dct_trj.iteritems():
            # dbg.M_DBG.debug("l_key:[{}]".format(l_key))
            # dbg.M_DBG.debug("l_trj:[{}]".format(l_trj))

            # é a trajetória selecionada ?
            if unicode(self.cbx_trj.currentText()) == unicode(l_trj):
                break

        # inicia o comando
        ls_cmd = "TRJ {}".format(l_key)

        # coloca o comando no label
        self.lbl_comando.setText(ls_cmd)

    # =============================================================================================
    # edição de campos
    # =============================================================================================

    # ---------------------------------------------------------------------------------------------
    @QtCore.pyqtSignature("int")
    def __on_cbx_currentIndexChanged(self, f_val):
        """
        DOCUMENT ME!
        """
        # atualiza comando
        self.__update_command()

# < the end >--------------------------------------------------------------------------------------
