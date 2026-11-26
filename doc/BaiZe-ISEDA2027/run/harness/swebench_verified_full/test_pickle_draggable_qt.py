import matplotlib
# Try to use Qt backend to reproduce the error
try:
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    import pickle
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

    fig = plt.figure()
    ax = fig.add_subplot(111)

    time=[0,1,2,3,4]
    speed=[40,43,45,47,48]

    ax.plot(time,speed,label="speed")

    leg=ax.legend()
    leg.set_draggable(True)

    print("Attempting to pickle figure with Qt backend...")
    pickle_data = pickle.dumps(fig)
    print(f"Pickle successful, size: {len(pickle_data)} bytes")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
