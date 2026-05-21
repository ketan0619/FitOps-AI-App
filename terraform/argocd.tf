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


resource "kubernetes_service_v1" "argocd_server_nlb" {
  metadata {
    name      = "argocd-server"
    namespace = "argocd"
    
    labels = {
      "app.kubernetes.io/component" = "server"
      "app.kubernetes.io/name"      = "argocd-server"
      "app.kubernetes.io/part-of"   = "argocd"
    }

    annotations = {
      # This forces EKS to provision a high-performance Network Load Balancer
      "service.beta.kubernetes.io/aws-load-balancer-type" = "nlb"
    }
  }

  spec {
    selector = {
      "app.kubernetes.io/name" = "argocd-server"
    }

    port {
      name        = "http"
      port        = 80
      target_port = 8080
      protocol    = "TCP"
    }

    port {
      name        = "https"
      port        = 443
      target_port = 8080
      protocol    = "TCP"
    }

    type = "LoadBalancer"
  }
}
