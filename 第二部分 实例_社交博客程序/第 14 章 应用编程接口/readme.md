# 第 14 章 应用编程接口

最近几年,Web 程序有种趋势,那就是业务逻辑被越来越多地移到了客户端一侧,开创出 了一种称为富互联网应用(Rich Internet Application,RIA)的架构。在RIA中,服务器的 主要功能(有时是唯一功能)是为客户端提供数据存取服务。在这种模式中,服务器变成 了 Web 服务或应用编程接口`(Application Programming Interface,API)`。

RIA可采用多种协议与Web服务通信。远程过程调用`(Remote Procedure Call,RPC)`协议, 例如 `XML-RPC`,及由其衍生的简单对象访问协议`(Simplified Object Access Protocol,SOAP)`, 在几年前比较受欢迎。最近,表现层状态转移`(Representational State Transfer,REST)`架构崭 露头角,成为 Web 程序的新宠,因为这种架构建立在大家熟识的万维网基础之上。

Flask 是开发 REST 架构 Web 服务的理想框架,因为 Flask 天生轻量。

## 14.1 REST简介



