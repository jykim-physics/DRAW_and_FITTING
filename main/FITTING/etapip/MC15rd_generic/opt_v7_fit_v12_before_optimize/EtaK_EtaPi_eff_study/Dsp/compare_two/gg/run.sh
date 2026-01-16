#!/bin/bash

# 1. 이미지 파일명 앞에 붙을 프리픽스 설정
img_prefix="Dsp_etapip_gg"

# 2. 변수 리스트 정의 (포맷: "변수명|min|max|표시이름|범례위치|Log사용여부")
VARIABLES=(
  "BDT|0|1.0|BDT|left|False"
  "Dp_cosHelicityAngleMomentum|-1|1|cosHel(D^{+}_{(s)})|right|False"
  "etapip_Eta_Easym|0|1|abs((E_{#gamma_{1}} - E_{#gamma_{2}}) /(E_{#gamma_{1}} + E_{#gamma_{2}}))|right|False"
  "Dp_cosAngleBetweenMomentumAndVertexVectorInXYPlane|-1|1|cos#theta_{XY}|right|True"
  "Dp_dz|-0.2|0.4|dz(D^{+}_{(s)})|right|False"
  "Pip_dr|0|0.1|dr(h^{+})|right|False"
  "Dp_CMS_p|2.5|5.2|p^{*}(D^{+}_{(s)})|right|False"
)

echo ">>> Starting plotting for ${#VARIABLES[@]} variables..."

# 3. 루프를 돌며 Python 스크립트 실행
for entry in "${VARIABLES[@]}"; do
    # IFS(Internal Field Separator)를 '|'로 설정하여 문자열 분리
    IFS="|" read -r var_name min_bin max_bin display_name legend_loc use_log_y <<< "$entry"

    # 출력 파일명 생성 (예: etapip_pipipi_BDT.png)
    output_fname="${img_prefix}_${var_name}.png"

    echo "--------------------------------------------------"
    echo "Drawing: $var_name"
    echo "Output : $output_fname"

    # Python 스크립트 실행 (인자 순서 주의)
    # 인자 순서: var_name, min, max, display_name, output_fname, use_log_y, legend_loc
    python3 run.py \
        "$var_name" \
        "$min_bin" \
        "$max_bin" \
        "$display_name" \
        "$output_fname" \
        "$use_log_y" \
        "$legend_loc"

done

echo "--------------------------------------------------"
echo ">>> All plots are generated successfully!"
