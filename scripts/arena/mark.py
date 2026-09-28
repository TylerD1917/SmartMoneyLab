#!/usr/bin/env python3
"""Aggiornamento settimanale del NAV.

Non e' piu' una singola marcatura: delega a nav_daily, che ricostruisce il NAV di
ogni giorno di borsa dalle chiusure ufficiali. Il vecchio comportamento (un solo
punto a settimana, preso all'ultimo prezzo disponibile nel momento in cui girava
la Action, quindi intraday a mercato aperto) produceva valori non riproducibili e
curve a pendenza costante fra un lunedi' e l'altro.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arena_core as ac
import nav_daily as nd


def mark(cfg):
    nd.rebuild(cfg, write=True)


if __name__ == "__main__":
    mark(ac.load_config())
