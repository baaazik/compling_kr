FROM nlpub/tomita

RUN apt update && apt install  openssh-server sudo -y

RUN \
    mkdir /var/run/sshd \
    mkdir -p /root/.ssh

COPY ./id_rsa.pub /root/.ssh/authorized_keys

EXPOSE 22
CMD ["/usr/sbin/sshd","-D"]
