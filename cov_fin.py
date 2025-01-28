import streamlit as st
from pdf2image import convert_from_path
st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stHeader"] {
    display: none;
}
[data-testid="stToolbar"] {
    display: none;
}
[data-testid="stImage"] {
    text-align: center; 
}
[data-testid="stImage"] > img {
    margin: 0 auto;
}
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px; /* Trochę wyższe, jeśli chcesz zmieścić dwie linie */
    background-color: #FFFFFF;
    border-bottom: 1px solid #DDDDDD;
    padding: 5px 10px; /* zmniejszone paddingi, by się wszystko zmieściło */
    z-index: 99999;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Możesz dodać drobniejsze pismo dla opisu badania */
.top-bar .subtitle {
    font-size: 0.85rem; /* np. 85% normalnego rozmiaru */
    color: #444;        /* ciemnoszary */
    line-height: 1;     /* zbite w pionie */
}

.main-content {
    margin-top: 15px; 
}
.main-content img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
#MainMenu {
    visibility: hidden;
}
footer {
    visibility: hidden;
}
</style>

<div class="top-bar">
    <!-- Lewa część: tytuł + krótki opis badania -->
    <div>
        <strong>COVID-19 SIRD</strong><br>
        <span class="subtitle">Implementacja badania "On automatic calibration of the SIRD epidemiological model for COVID-19 data in Poland" + poszerzenie zakresu badań dla innych krajów.</span>
    </div>
    <!-- Prawa część: link do repo -->
    <div>
        <a href="https://github.com/twoj_link_do_repo" target="_blank">Kod źródłowy</a>
    </div>
</div>

<div class="main-content">
""", unsafe_allow_html=True)

import streamlit as st
import io, base64
from pdf2image import convert_from_path

def display_pdf_as_images(pdf_file, width=850):
    # Konwertujemy PDF na listę obiektów PIL (poszczególne strony)
    images = convert_from_path(pdf_file)

    # Dla każdej strony tworzymy <img> z wbudowaną treścią base64.
    for img in images:
        # Zamieniamy obiekt PIL na bajty PNG w pamięci
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        
        # Kodujemy w base64 i wstawiamy do HTML-a
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="data:image/png;base64,{img_b64}"
                     style="max-width:{width}px; margin:0 auto;"/>
            </div>
            """,
            unsafe_allow_html=True
        )


if "kraj" not in st.session_state:
    st.session_state.kraj = None

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Izrael"):
        st.session_state.kraj = "Izrael"
with col2:
    if st.button("Polska"):
        st.session_state.kraj = "Polska"
with col3:
    if st.button("Niemcy"):
        st.session_state.kraj = "Niemcy"
with col4:
    if st.button("Austria"):
        st.session_state.kraj = "Austria"
with col5:
    if st.button("Włochy"):
        st.session_state.kraj = "Włochy"
if st.session_state.kraj == "Włochy":
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Dzienny rozkład nowych przypadków/zgonów/zmiany w liczbie aktywnych"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/daily.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/params1_20102020.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-10-21 do 2021-08-16"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/params_2_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/plot_fitting_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/plot_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2020-05-10 do 2020-06-13 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/1000repetitions_2020_05_10.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2021-04-04 do 2021-05-07 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Italy/1000_repetitions_2021_.pdf", width=850)

if st.session_state.kraj == "Izrael":
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Dzienny rozkład nowych przypadków/zgonów/zmiany w liczbie aktywnych"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/daily.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/params1_20102020.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-10-21 do 2021-08-16"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/params_2_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/plot_fitting_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/plot_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2020-05-10 do 2020-06-13 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/1000repetitions_2020_05_10.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2021-04-04 do 2021-05-07 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Izrael/1000_repetitions_2021_.pdf", width=850)

elif st.session_state.kraj == "Polska":
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Dzienny rozkład nowych przypadków/zgonów/zmiany w liczbie aktywnych"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/daily.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/params_1_before_20_10_2020.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-10-21 do 2021-08-16"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/params_2_after_20_10_2020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/minmax_before_20_10_2020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/minmax_after_20_10_2020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2020-05-10 do 2020-06-13 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/1000_repetitions_fitting_2020_05_10.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2021-04-04 do 2021-05-07 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Poland/1000_repetitions_fitting_2021_04_04.pdf", width=850)

elif st.session_state.kraj == "Niemcy":
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Dzienny rozkład nowych przypadków/zgonów/zmiany w liczbie aktywnych"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/daily.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/params1_20102020.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-10-21 do 2021-08-16"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/params_2_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/plot_fitting_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/plot_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2020-05-10 do 2020-06-13 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/1000repetitions_2020_05_10.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2021-04-04 do 2021-05-07 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Germany/1000_repetitions_2021_.pdf", width=850)

elif st.session_state.kraj == "Austria":
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Dzienny rozkład nowych przypadków/zgonów/zmiany w liczbie aktywnych"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/daily.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/params1_20102020.pdf", width=850)
    
    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Rozkład parametrów w okresie 2020-10-21 do 2021-08-16"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/params_2_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/plot_fitting_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Obwiednia minmax w okresie 2020-03-18 do 2020-10-20"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/plot_after_20102020.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2020-05-10 do 2020-06-13 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/1000repetitions_2020_05_10.pdf", width=850)

    st.markdown(
        "<h4 style='text-align: center; font-size:18px;'>"
        "Wynik 1000 dopasowan w okresie 2021-04-04 do 2021-05-07 + 21-dniowe przewidywanie"
        "</h4>", 
        unsafe_allow_html=True
    )
    display_pdf_as_images("results/Austria/1000_repetitions_2021_.pdf", width=850)

st.markdown("</div>", unsafe_allow_html=True)
