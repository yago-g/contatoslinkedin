#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[ ]:


import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from time import sleep
from selenium.webdriver.common.by import By
import re
import pandas as pd


# # Login no LinkedIn

# In[ ]:


navegador = webdriver.Chrome()
navegador.get('https://br.linkedin.com/')
WebDriverWait(navegador, 50).until(EC.url_to_be("https://www.linkedin.com/feed/?trk=homepage-basic_sign-in-submit"))
navegador.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")


# # Exibição de todas as conexões

# In[ ]:


SCROLL_PAUSE_TIME = 5
last_height = navegador.execute_script("return document.body.scrollHeight")
while True:
    navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(SCROLL_PAUSE_TIME)
    new_height = navegador.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        try:
            exibir_mais_resultados = navegador.find_elements(By.TAG_NAME, "button")
            botao_mais_resultados = exibir_mais_resultados[167]
            botao_mais_resultados.click()
            sleep(SCROLL_PAUSE_TIME)
        except:
            perfis = navegador.find_elements(By.CLASS_NAME, "mn-connection-card__name ")
            break
    last_height = new_height


# In[ ]:


perfis_extraidos = []
perfis_exibidos = navegador.find_elements(By.CLASS_NAME, "artdeco-list")

for perfil in perfis_exibidos[0:50]:
    link = perfil.find_element(By.TAG_NAME, "a")
    link = link.get_attribute('href')
    perfis_extraidos.append(link) 


# # Extração das informações de contato das conexões
# 

# In[ ]:


base_de_nomes = []
base_de_telefones = []
 
for perfil in perfis_extraidos:
    navegador.get(perfil)
    contato_perfil = WebDriverWait(navegador, 50).until(
        EC.presence_of_element_located((By.ID, "top-card-text-details-contact-info")))
    contato_perfil.click()
    infocontato_perfil = WebDriverWait(navegador, 50).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pv-contact-info__ci-container")))
    texto1_infocontato_perfil = navegador.find_elements(By.ID, "pv-contact-info")
    texto2_infocontato_perfil = navegador.find_elements(By.CLASS_NAME, "pv-contact-info__ci-container")
    nome_perfil = texto1_infocontato_perfil[0].text
    base_de_nomes.append(nome_perfil)
    telefone_perfil = texto2_infocontato_perfil[1].text
    match = re.search(r'\d+', telefone_perfil)
    if match and len(match.group()) == 11:
        telefone_perfil = int(match.group())
        base_de_telefones.append(telefone_perfil)
    else:
        base_de_telefones.append(0)
    navegador.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(3)


# # Exportação dos contatos para Excel

# In[ ]:


lista_de_contatos_1 = pd.DataFrame(base_de_nomes)
lista_de_contatos_1 = lista_de_contatos_1.rename(columns={0: "Nome"})
lista_de_contatos_2 = pd.DataFrame(base_de_telefones)
lista_de_contatos_2 = lista_de_contatos_2.rename(columns={0: "Telefone"})
lista_de_contatos_final = pd.concat([lista_de_contatos_1, lista_de_contatos_2], axis=1)

lista_de_contatos_final.to_excel("contatos_linkedin.xlsx", index=False)


# # Fim
