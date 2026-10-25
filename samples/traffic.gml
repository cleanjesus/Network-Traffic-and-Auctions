graph [
  directed 1
  node [ id 0 label "S" ]
  node [ id 1 label "U" ]
  node [ id 2 label "V" ]
  node [ id 3 label "T" ]
  edge [ source 0 target 1 a 0.01 b 0 ]
  edge [ source 1 target 3 a 0 b 45 ]
  edge [ source 0 target 2 a 0 b 45 ]
  edge [ source 2 target 3 a 0.01 b 0 ]
  edge [ source 1 target 2 a 0 b 0 shortcut 1 ]
]
