## Workflows hydrologische basis data waterschappen: o.a. voorbewerking, locaties duikers, afwateringseenheden, stroomgebieden, orde-codering

[Bekijk de uitgebreide documentatie via de read-the-docs](https://sweco-nl.github.io/generator_drainage_units/)

### Algemeen
Deze python-toolbox is opgezet door Sweco Nederland binnen twee opdrachten met als doel om uit hydrologische basisdata van de waterschappen netwerk-analyses uit te voeren. Er is voor gekozen om open-source te werken. Er is geprobeerd om gestructureerd deze python-toolbox op te zetten en testdata en documentatie toe te voegen.

### Waterschap Vallei & Veluwe
De wens om op basis van een raster met een hoogtemodel (maaiveld of grondwaterstand) en een waternetwerk stroomgebiedjes af te leiden, ook wel afwateringseenheden of hydrologische eenheden genoemd. Middels codering zou het mogelijk moeten zijn om deze te aggregeren tot elk gewenst niveau:
- **generator_culvert_locations**: voortbouwend op een al bestaande 'duikergenerator' worden de locaties van duikers bepaald. Dit gebeurd op basis van (configureerbare) regels, die rekening houden met kruizingen van wegen en peilgebiedsgrenzen, de lengte van de duiker (hoe lager, hoe beter) en de richting van de duiker ten opzichte van de watergang (zelfde hoek heeft voorkeur). 
- **generator_order_levels**: bepalen van de orde en de orde-codering van het netwerk en daarmee voor de afwaterende eenheden (conform [Leidraad Harmoniseren Afvoergebieden](https://kennis.hunzeenaas.nl/file_auth.php/hunzeenaas/a/aa/Leidraden_Harmoniseren_Afvoergebieden_v1.1.pdf))
- **generator_drainage_units**: workflow voor het genereren van afwateringseenheden: op basis van een GHG raster 25x25m de afvoerrichting bepalen en daarmee de afwaterende eenheden. Dit met behulp van o.a. [RESPHIGI](https://gitlab.com/deltares/imod/respighi) en [PyFlwDir van Deltares](https://github.com/Deltares/pyflwdir)

### Waterschap Aa en Maas
De vraag om op basis van benedenstroomse uitstroompunten (deel)stroomgebieden te genereren.
- **generator_network_lumping**: Toolbox om voor gegeven uitstroompunten het bovenstroomse netwerk te lumpen en afvoergebieden of (deel)stroomgebieden te genereren.



### Installatie environment
We gebruiken pixi om de environment op orde te houden. Installatie van pixi (prefix.dev) kan via de Windows Powershell:
```
iwr -useb https://pixi.sh/install.ps1 | iex
```
Bouw de environment op op basis van het bestand pyproject.toml door in de projectfolder via de terminal te draaien:
```
pixi install
```
Om te voorkomen dat de output en metadata van de jupyter notebooks wordt gecommit, draai dit:
```
git config filter.strip-notebook-output.clean 'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR'
```
We gebruiken ruff voor de code-formatting. Installatie ruff via:
```
pixi global install ruff
```
Gebruik ruff:
```
ruff format
```
