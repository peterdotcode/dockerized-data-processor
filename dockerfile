# Ubuntu as OS image
FROM ubuntu
# Updating Ubuntu packages
RUN apt-get update && yes|apt-get upgrade
# Adding wget and bzip2
RUN apt-get install -y wget bzip2
# Anaconda installing
RUN wget  https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh
RUN bash Anaconda3-2018.12-Linux-x86_64.sh -b
RUN rm Anaconda3-2018.12-Linux-x86_64.sh
# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH
# Updating Anaconda packages
# Configuring access to Jupyter
RUN mkdir /opt/notebooks
COPY . /opt/notebooks/

RUN jupyter notebook --generate-config --allow-root
# Use password "root" to login
RUN echo "c.NotebookApp.password = u'sha1:6a3f528eec40:6e896b6e4828f525a6e20e5411cd1c8075d68619'" >> /root/.jupyter/jupyter_notebook_config.py
# Jupyter listens port: 8888
EXPOSE 8888
# Run Jupytewr notebook as Docker main process
CMD ["jupyter", "notebook", "--allow-root", "--notebook-dir=/opt/notebooks", "--ip='0.0.0.0'", "--port=8888", "--no-browser"]
