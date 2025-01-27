.. DrainageUnits documentation master file, created by
   sphinx-quickstart on Wed Dec 18 09:19:01 2024.


Generator Drainage Units: Workflows voor hydrologische basisdata waterschappen
============================================================================================================================

- `GitHub-repository GeneratorDrainageUnits <https://github.com/Sweco-NL/generator_drainage_units>`_

o.a. workflows voor voorbewerking waternetwerk, verbinden c-watergangen middels duikers, afleiden van afwateringseenheden en stroomgebieden, automatische toekennen van orde-codering. 


Algemeen
----------------------------
Deze python-toolbox is opgezet door Sweco Nederland binnen twee losse opdrachten voor waterschap Aa en Maas en Vallei & Veluwe met als doel om uit hydrologische basisdata van de waterschappen netwerk-analyses uit te voeren. We bundelen hierbij de workflows in een public repository inclusief testdata, voorbeeld-scripts en documentatie.

Voor meer informatie: 

- Harmen van de Werfhorst (Waterschap Vallei & Veluwe)
- Joachim Hunink (Waterschap Aa & Maas)
- Harm Nomden / Joren van Os / Lieke van Haastregt (Sweco)

.. image:: _static/logos.jpg
   :alt: Opdrachtgever + Sweco
   :width: 800px
   :align: center

Hier onder is kort beschreven welke workflows zijn opgezet. Voor een uitgebreide uitleg zie `beschrijving workflows <description_workflows.html>`_

Waterschap Aa & Maas
----------------------------
De vraag om op basis van benedenstroomse uitstroompunten (deel)stroomgebieden te genereren.

- `GeneratorNetworkLumping <description_workflows.html#generatornetworklumping-workflow-aggregeren-deel-stroomgebieden>`_: workflow om voor opgegeven uitstroompunten het bovenstroomse watersysteem inclusief afwateringseenheden te lumpen (aggregeren) om stroomgebieden of deelstroomgebieden te genereren. Hierbij wordt overlap gedetecteerd en kan men aangeven hoe de deelgebieden verdeeld worden.


Waterschap Vallei & Veluwe
----------------------------
De vraag om afvoergebieden af te leiden tot op het diepste detailniveau op basis van een raster met een hoogtemodel (maaiveld of in dit geval grondwaterstand GHG) en een gegeven waternetwerk. Deze afvoergebiedjes worden ook wel afwateringseenheden of hydrologische eenheden genoemd. Middels netwerk-analyse en codering is het mogelijk om deze te aggregeren tot elk gewenst niveau:

- `GeneratorCulvertLocations <description_workflows.html#generatorculvertlocations-workflow-duiker-locaties>`_: workflow die voortbouwt op een al bestaande 'duikergenerator' van het waterschap waarin de locaties van duikers voor de C-watergangen worden bepaald. Dit gebeurt op basis van (configureerbare) regels, die rekening houden met kruisingen van (spoor)wegen en peilgebiedsgrenzen, de lengte van de duiker (hoe korter, hoe beter) en de richting van de duiker ten opzichte van de watergang (zelfde hoek heeft voorkeur). 

- `GeneratorOrderLevels <description_workflows.html#generatororderlevels-workflow-orde-codering>`_: workflow voor het bepalen van orde nummers en de orde-codering van iedere watergang en daarmee voor de afwaterende eenheden (conform `Leidraad Harmoniseren Afvoergebieden <https://kennis.hunzeenaas.nl/file_auth.php/hunzeenaas/a/aa/Leidraden_Harmoniseren_Afvoergebieden_v1.1.pdf>`_), op basis van de codering kan eenvoudig geaggregeerd worden. Ook worden hier de C-watergangen (niet hoofdwatergangen) meegenomen in de analyse.

- `GeneratorDrainageUnits <description_workflows.html#generatordrainageunits-workflow-afwateringseenheden>`_: workflow voor het genereren van afwateringseenheden: op basis van een GHG raster 25x25m de afvoerrichting bepalen en daarmee de afwaterende eenheden. Dit met behulp van andere open source packages zoals `PyFlwDir van Deltares <https://github.com/Deltares/pyflwdir>`_


Inhoud
----------------------------
.. toctree::
   :maxdepth: 2
   
   Installatie en gebruik <getting_started>
   Beschrijving workflows <description_workflows>
   API documentatie <api_docs>

