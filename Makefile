all:
	rm -f pseyfert.aux pseyfert.toc pseyfert.snm
	xelatex pseyfert.tex
	xelatex pseyfert.tex
	xelatex pseyfert.tex

quick:
	xelatex pseyfert.tex
clean:
	rm -rf pseyfert.aux pseyfert.log pseyfert.nav pseyfert.out pseyfert.snm pseyfert.toc pseyfert.vrb

printviews:
	pdfnup --nup '2x2' pseyfert.pdf
	gs -sOutputFile=pseyfert-nup-gray.pdf -sDEVICE=pdfwrite -sColorConversionStrategy=Gray -dProcessColorModel=/DeviceGray -dCompatibilityLevel=1.4 -dNOPAUSE -dBATCH pseyfert-nup.pdf

include aspell.mk

# Makefile for pseyfert/slide_template.
# Copyright (C) 2017  Paul Seyfert <pseyfert@cern.ch>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
