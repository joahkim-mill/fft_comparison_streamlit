import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
from scipy.fft import fft, fftfreq
import io 

def is_it_good(x, y):

        threshold_y = [0]
        threshold_y1 = [0.5 for x in x[1:2100]]
        threshold_y2 = -(0.3/340) * x[2100:] + (0.5 + 0.3 / 350 * 210)
       
        threshold_y.extend(threshold_y1)
        threshold_y.extend(threshold_y2)

        y1 = y[1:2100]
        crossed_1 = y1[y[1:2100]>threshold_y[1:2100]]

        y2 = y[2100:]
        crossed_2 = y2[y[2100:] > threshold_y[2100:]]

        if len(crossed_1) > 1 and max(crossed_1) > 0.9:
            # result = "FAIL"
            result = 0
        elif len(crossed_2) > 1:
            # result = "FAIL"
            result = 0
        elif (len(crossed_1) + len(crossed_2)) == 0: # CLEAN PASS
            result = 2
        else :
            # result = "PASS"
            result = 1 # "DIRTY"/IFFY PASS

        return result

fig = go.Figure()
# df = pd.DataFrame(columns=["Fan", "Result"])
df = {"Fan": "Result"}
pio.templates.default = "plotly"  #allows color on plots when saving as html
st. set_page_config(initial_sidebar_state="collapsed") #initializes sidebar as closed
with st.sidebar:
    add_title = st.text_input("Plot Title", 'FFT Comparison - 100pwm') # can input new plot title
    add_files = st.file_uploader("Choose CSV file(s)", accept_multiple_files=True) # add files to plot

for uploaded_file in add_files:
    # with st.sidebar:
    #     dataname = st.text_input(uploaded_file.name) # can input new trace name
    dataname = uploaded_file.name[4:9]

    fft_data = pd.read_csv(uploaded_file)
    fft_data.columns = ['index', 'time', 'x_accel', 'y_accel', 'z_accel']

    t = np.asarray(fft_data["time"])
    az = np.asarray(fft_data["z_accel"])

    N = len(t)
    sample_rate = 1100 # Hz 
    T = 1/sample_rate 
    yf_z = fft(az)
    xf_z = fftfreq(N, T)[:N//2]
    y_z = 2.0/N * abs(yf_z[0:N//2])
    result = is_it_good(xf_z, y_z)
    df[dataname] = result
    # df = df.append(pd.DataFrame({f"{dataname}": result}, ignore_index=True))

    # if dataname=="":
    #     dataname = uploaded_file.name
    fig.add_trace(go.Scatter(x=xf_z[1:], y=y_z[1:], line_shape='linear', name=dataname, line=dict(width=0.8, ), ) )

thsd_1_x = [0, 200]
thsd_1_y = [0.5, 0.5]
thsd_2_x = [201, 550]
thsd_2_y = [0.5, 0.2]
thsd_3_x = [0, 550]
thsd_3_y = [0.9, 0.9]
fig.add_trace(go.Scatter(x=thsd_1_x, y=thsd_1_y, name='Threshold 1', line=dict(color='gray', dash='dash'), mode='lines'))
fig.add_trace(go.Scatter(x=thsd_2_x, y=thsd_2_y, name='Threshold 2', line=dict(color='gray', dash='dash'), mode='lines'))
fig.add_trace(go.Scatter(x=thsd_3_x, y=thsd_3_y, name='Hard Stop', line=dict(color='black', dash='dashdot', width=1), mode='lines'))

fig.update_layout(title=add_title, xaxis_title='Hz', 
                plot_bgcolor='white', height=600, width=900, )
fig.update_yaxes(range=[0, 1])
fig.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
fig.update_yaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)

st.plotly_chart(fig)
st.dataframe(df)
with st.sidebar: # create button to download plot as html
    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    html_bytes = buffer.getvalue().encode()

    st.download_button(
        label='Download HTML',
        data=html_bytes,
        file_name=f'{add_title}.html',
        mime='text/html'
    )
# fig.show()
