import numpy as np
import pychemia
import scipy.optimize


class LennardJones:

    def __init__(self, structure, ljparams=None, dt=1, tolerance=1):
        self.initial_structure = structure
        self.structure = structure.copy()

        if ljparams is None:
            ljparams = {}
            for i in self.structure.species:
                for j in self.structure.species:
                    ljparams[i+'-'+j] = {'sigma': 1.0, 'epsilon': 1.0}
        self.ljparams = ljparams
        self.dt = dt
        self.tolerance = tolerance

    def get_forces(self):
        ret = np.zeros((self.structure.natom, 3))
        for i in range(self.structure.natom-1):
            for j in range(i+1, self.structure.natom):
                vector = self.structure.positions[j] - self.structure.positions[i]
                distance = np.linalg.norm(vector)
                magnitude = self.magforce(distance, i, j)
                ret[i] += magnitude*vector/distance
                ret[j] -= magnitude*vector/distance
        return ret

    def get_magnitude_forces(self):
        return pychemia.utils.mathematics.length_vectors(self.get_forces())

    def magforce(self, distance, i, j):
        sigma, epsilon = self.get_sigma_epsilon(i, j)
        sr6 = (sigma/distance)**6
        return 24*epsilon/distance * (2.0*sr6**2 - sr6)

    def steepest_descent(self):
        forces = self.get_forces()
        while np.max(self.get_magnitude_forces()) > self.tolerance:
            for i in range(self.structure.natom):
                mass = pychemia.utils.periodic.mass(self.structure.symbols[i])
                self.structure.positions[i] += 0.5*forces[i]/mass * self.dt**2

            forces = self.get_forces()
            print self.get_magnitude_forces()

    def get_sigma_epsilon(self, i, j):
        specie1 = self.structure.symbols[i]
        specie2 = self.structure.symbols[j]
        sort_species = [specie1, specie2]
        sort_species.sort()

        sigma = self.ljparams[sort_species[0]+'-'+sort_species[1]]['sigma']
        epsilon = self.ljparams[sort_species[0]+'-'+sort_species[1]]['epsilon']

        return float(sigma), float(epsilon)

    def get_energy(self):
        ret = 0
        for i in range(self.structure.natom-1):
            for j in range(i+1, self.structure.natom):
                vector = self.structure.positions[j] - self.structure.positions[i]
                distance = np.linalg.norm(vector)
                sigma, epsilon = self.get_sigma_epsilon(i, j)
                sr6 = (sigma/distance)**6
                ret += 4*epsilon*(sr6**2 - sr6)
        return ret

    def local_minimization(self, method='BFGS', gtol=1E-4, soft_max_ncalls=5, hard_max_ncalls=10):

        def energy(x):
            pos = np.array(x).reshape((-1, 3))
            n = len(pos)
            st = pychemia.Structure(positions=pos, symbols=n*['C'], periodicity=False)
            lj = pychemia.code.lennardjones.LennardJones(structure=st)
            return lj.get_energy()

        def forces(x):
            pos = np.array(x).reshape((-1, 3))
            n = len(pos)
            st = pychemia.Structure(positions=pos, symbols=n*['C'], periodicity=False)
            lj = pychemia.code.lennardjones.LennardJones(structure=st)
            return lj.get_forces().flatten()
        if method in ['Nelder-Mead', 'Powell']:
            jac = None
        else:
            jac = forces

        x0 = self.structure.positions.flatten()

        hard_call = 0
        soft_call = 0
        while True:

            res = scipy.optimize.minimize(energy, x0, method=method, jac=jac,
                                          options={'maxiter': 100, 'gtol': 0.1*gtol, 'disp': False})
            maxforce = np.max(np.apply_along_axis(np.linalg.norm, 1, np.array(res.jac).reshape((-1, 3))))
            print 'MaxForce= %9.3E  Value= %7.3f' % (maxforce, res.fun)

            x0 = res.x
            soft_call += 1
            hard_call += 1
            if maxforce < gtol:
                print 'The tolerance was reached: maxforce= %9.3E gtol= %9.3E' % (maxforce, gtol)
                break
            if soft_call > soft_max_ncalls:
                print 'Anomalous condition, maxforce= %9.3E gtol= %9.3E' % (maxforce, gtol)
                pos = np.array(x0).reshape((-1, 3))
                mindis = np.min((scipy.spatial.distance_matrix(pos, pos)+100*np.eye(len(pos))).flatten())
                x0 = (1.0/mindis * pos).flatten()
                soft_call = 0
            if hard_call > hard_max_ncalls:
                print 'Could not reach target forces, maxforce= %9.3E gtol= %9.3E' % (maxforce, gtol)
                print 'Hard limit reached, aborting local minimization'
                break

        return res
