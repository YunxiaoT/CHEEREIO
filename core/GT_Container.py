import numpy as np
from glob import glob
import settings_interface as si 
from datetime import date,datetime,timedelta
from GC_Translator import GC_Translator

#Lightweight container for GC_Translators; used to combine columns, update restarts, and diff columns.
class GT_Container(object):
	def __init__(self,timestamp,getAssimColumns=True, constructStateVecs=True):
		spc_config = si.getSpeciesConfig()
		path_to_ensemble = f"{spc_config['MY_PATH']}/{spc_config['RUN_NAME']}/ensemble_runs"
		self.path_to_scratch = f"{spc_config['MY_PATH']}/{spc_config['RUN_NAME']}/scratch"
		if getAssimColumns:
			npy_column_files = glob(f'{self.path_to_scratch}/**/*.npy',recursive=True)
			npy_col_names = [file.split('/')[-1] for file in npy_column_files]
			npy_columns = [np.load(file) for file in npy_column_files]
			self.columns = dict(zip(npy_col_names,npy_columns))
		else:
			self.columns = None
		subdirs = glob(f"{path_to_ensemble}/*/")
		subdirs.remove(f"{path_to_ensemble}/logs/")
		dirnames = [d.split('/')[-2] for d in subdirs]
		subdir_numbers = [int(n.split('_')[-1]) for n in dirnames]
		ensemble_numbers = []
		self.gt = {}
		self.observed_species = spc_config['OBSERVED_SPECIES']
		for ens, directory in zip(subdir_numbers,subdirs):
			if ens!=0:
				self.gt[ens] = GC_Translator(directory, timestamp, constructStateVecs)
				ensemble_numbers.append(ens)
		self.ensemble_numbers=np.array(ensemble_numbers)
	#Gets saved column and compares to the original files
	def constructColStatevec(self,latind,lonind):
		firstens = self.ensemble_numbers[0]
		col1indvec = self.gt[firstens].getColumnIndicesFromFullStateVector(latind,lonind)
		backgroundEnsemble = np.zeros((len(col1indvec),len(self.ensemble_numbers)))
		backgroundEnsemble[:,firstens-1] = self.gt[firstens].getStateVector()[col1indvec]
		for i in self.ensemble_numbers:
			if i!=firstens:
				colinds = self.gt[i].getColumnIndicesFromFullStateVector(latind,lonind)
				backgroundEnsemble[:,i-1] = self.gt[i].getStateVector()[colinds]
		return backgroundEnsemble
	def diffColumns(self,latind,lonind):
		filenames = list(self.columns.keys())
		substr = f'lat_{latind}_lon_{lonind}.npy'
		search = [i for i in filenames if substr in i]
		saved_col = self.columns[search[0]]
		backgroundEnsemble = self.constructColStatevec(latind,lonind)
		diff = saved_col-backgroundEnsemble
		return [saved_col,backgroundEnsemble,diff]
	def constructBackgroundEnsemble(self):
		self.backgroundEnsemble = np.zeros((len(self.gt[1].getStateVector()),len(self.ensemble_numbers)))
		for i in self.ensemble_numbers:
			self.backgroundEnsemble[:,i-1] = self.gt[i].getStateVector()
	def reconstructAnalysisEnsemble(self):
		self.analysisEnsemble = np.zeros((len(self.gt[1].getStateVector()),len(self.ensemble_numbers)))
		for name, cols in zip(self.columns.keys(),self.columns.values()):
			split_name = name.split('_')
			latind = int(split_name[-3])
			lonind = int(split_name[-1].split('.')[0])
			colinds = self.gt[1].getColumnIndicesFromFullStateVector(latind,lonind)
			self.analysisEnsemble[colinds,:] = cols
	def updateRestartsAndScalingFactors(self):
		for i in self.ensemble_numbers:
			self.gt[i].reconstructArrays(self.analysisEnsemble[:,i-1])
	def saveRestartsAndScalingFactors(self,saveRestart=True, saveEmissions=True, saveSpecial=True):
		for i in self.ensemble_numbers:
			if saveRestart:
				self.gt[i].saveRestart()
			if saveEmissions:
				self.gt[i].saveEmissions()
			if saveSpecial:
				self.gt[i].saveSpecial()
