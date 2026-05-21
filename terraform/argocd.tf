resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true

  values = [
    yamlencode({
      server = {
        service = {
          type = "LoadBalancer"
        }
      }
      configs = {
        params = {
          "server.insecure" = true
        }
      }
    })
  ]

  depends_on = [module.eks]
}


resource "kubernetes_manifest" "fitops_application" {
  manifest = yamldecode(file("${path.module}/../manifests/argocd/root-app.yml"))
  depends_on = [
    helm_release.argocd 
  ]
}
