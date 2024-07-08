import math

def Acp_and_AcpError_cal(Nsig, Nsig_cc, Nsig_err, Nsig_cc_err):
    Z = (Nsig - Nsig_cc)/(Nsig + Nsig_cc)
    dAcp_dNsig = Z * (2*Nsig_cc/ (Nsig**2 - Nsig_cc**2) ) * Nsig_err
    dAcp_DNsig_cc = - Z * (2*Nsig/ (Nsig**2 - Nsig_cc**2) ) * Nsig_cc_err

    dZ_square = dAcp_dNsig**2 + dAcp_DNsig_cc**2
    return Z, math.sqrt(dZ_square)

def Acp_cal(Nsig, Nsig_cc):
    Z = (Nsig - Nsig_cc)/(Nsig + Nsig_cc)

    return Z