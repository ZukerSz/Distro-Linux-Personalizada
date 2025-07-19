#!/bin/bash

# --- CONFIGURAÇÕES INICIAIS ---
# Garante que o script pare a execução se qualquer comando falhar.
set -e

# ===================================================================================
# SEÇÃO 1: ATUALIZAÇÃO E INSTALAÇÃO DE DEPENDÊNCIAS
# ===================================================================================
echo "Iniciando: Atualizando o sistema e instalando dependências..."
apt update
apt install -y python3-pygame python3-tk python3-pil.imagetk python3-matplotlib python3-pip
pip install customtkinter tkcalendar

# ===================================================================================
# SEÇÃO 2: INSTALAÇÃO DOS PROGRAMAS PYTHON
# ===================================================================================
echo "Instalando aplicações Python (Batalha Naval, NotesSyst, ToDoList)..."

# --- Criação dos diretórios de instalação ---
mkdir -p /opt/batalha-naval
mkdir -p /opt/notesyst
mkdir -p /opt/todolist
mkdir -p /usr/share/pixmaps

# --- Cópia dos arquivos dos programas ---
cp -r /root/meus-programas/batalha-naval/* /opt/batalha-naval/
cp -r /root/meus-programas/notesyst/* /opt/notesyst/
cp -r /root/meus-programas/todolist/* /opt/todolist/

# --- Criação dos executáveis (lançadores) em /usr/local/bin ---
echo '#!/bin/bash
cd /opt/batalha-naval/
python3 main.py' > /usr/local/bin/batalha-naval

echo '#!/bin/bash
cd /opt/notesyst/
python3 universidade.py' > /usr/local/bin/sistema-notas

echo '#!/bin/bash
cd /opt/todolist/
python3 todo.py' > /usr/local/bin/todolist

# --- Criação dos atalhos no menu de aplicativos (.desktop) ---
cat > /usr/share/applications/batalha-naval.desktop << EOF
[Desktop Entry]
Version=1.0
Name=Batalha Naval
Comment=Jogo de Batalha Naval em Python
Exec=batalha-naval
Icon=/usr/share/pixmaps/batalha-naval.png
Terminal=false
Type=Application
Categories=Game;
EOF

cat > /usr/share/applications/notesyst.desktop << EOF
[Desktop Entry]
Version=1.0
Name=NotesSyst
Comment=Sistema de gerenciamento de notas universitárias
Exec=sistema-notas
Icon=/usr/share/pixmaps/notesyst.png
Terminal=false
Type=Application
Categories=Office;Education;
EOF

cat > /usr/share/applications/todolist.desktop << EOF
[Desktop Entry]
Version=1.0
Name=ToDoList
Comment=Gerenciador de tarefas
Exec=todolist
Icon=/usr/share/pixmaps/todolist.png
Terminal=false
Type=Application
Categories=Office;Utility;
EOF

# --- Cópia dos ícones para os atalhos ---
cp /root/meus-programas/batalha-naval/navio.png /usr/share/pixmaps/batalha-naval.png
cp /root/meus-programas/notesyst/2.png /usr/share/pixmaps/notesyst.png
cp /root/meus-programas/todolist/5.png /usr/share/pixmaps/todolist.png

# --- Ajuste de permissões ---
chmod 755 /usr/local/bin/*
chmod 644 /usr/share/pixmaps/*.png
chmod 644 /usr/share/applications/*.desktop
update-desktop-database /usr/share/applications/

# --- Criação dos atalhos na Área de Trabalho para novos usuários ---
mkdir -p /etc/skel/Desktop
cp /usr/share/applications/*.desktop /etc/skel/Desktop/
chmod +x /etc/skel/Desktop/*.desktop

# ===================================================================================
# SEÇÃO 3: INSTALAÇÃO DE SOFTWARE ADICIONAL
# ===================================================================================
echo "Instalando softwares adicionais (Chrome, VSCode)..."
wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y /tmp/google-chrome-stable_current_amd64.deb

wget -O /tmp/vscode.deb "https://go.microsoft.com/fwlink/?LinkID=760868"
apt install -y /tmp/vscode.deb

# ===================================================================================
# SEÇÃO 4: LIMPEZA DE PACOTES E INSTALAÇÃO DE PACOTES DE CUSTOMIZAÇÃO
# ===================================================================================
echo "Removendo pacotes desnecessários..."
apt purge -y thunderbird hexchat pidgin parole rhythmbox xfburn gnome-mines gnome-sudoku simple-scan transmission-gtk
apt autoremove -y

echo "Instalando pacotes para customização visual..."
apt install -y git sassc libglib2.0-dev-bin qt5-style-kvantum papirus-icon-theme

# ===================================================================================
# SEÇÃO 5: INSTALAÇÃO E CONFIGURAÇÃO DO TEMA (ORCHIS)
# ===================================================================================
echo "Aplicando o tema Orchis-Dark..."

# --- Baixa e instala o tema ---
cd /tmp
git clone https://github.com/vinceliuice/Orchis-theme.git
cd Orchis-theme
./install.sh -c dark -t grey --tweaks black
cd /

# --- Garante que as pastas de configuração existam no /etc/skel ---
mkdir -p /etc/skel/.config/gtk-3.0/
mkdir -p /etc/skel/.config/Kvantum/
mkdir -p /etc/profile.d/

# --- Força o uso do Kvantum para aplicações Qt ---
cat > /etc/profile.d/qt-style.sh << EOF
export QT_STYLE_OVERRIDE=kvantum
EOF

# --- Configura o tema GTK padrão para novos usuários ---
cat > /etc/skel/.config/gtk-3.0/settings.ini << EOF
[Settings]
gtk-application-prefer-dark-theme=true
gtk-theme-name=Orchis-Grey-Dark
gtk-icon-theme-name=Papirus-Dark
gtk-font-name=Noto Sans 10
EOF

# --- Configura o tema do Kvantum padrão para novos usuários ---
cat > /etc/skel/.config/Kvantum/kvantum.kvconfig << EOF
[General]
theme=Orchis-Grey-Dark
EOF

# ===================================================================================
# SEÇÃO 6: LIMPEZA FINAL
# ===================================================================================
echo "Finalizando e limpando arquivos temporários..."
rm -rf /tmp/Orchis-theme
rm -f /tmp/google-chrome-stable_current_amd64.deb
rm -f /tmp/vscode.deb

echo "Script feito!"