const dns = require('dns').promises;
const geoip = require('geoip-lite');
const config = require('./config')

Resolver = dns.Resolver;
resolver = new Resolver();
resolver.setServers(config.dnsServers);

function countryOf(ip){
    let geo = geoip.lookup(ip);
    return geo == null ? 'unknown' : geo.country
}

module.exports={
    async get(name){
        let domainReg = /[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+.?/g
        let ipReg = /((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}/
        if(ipReg.test(name)){
            return countryOf(name)
        }else if(domainReg.test(name)){
            try{
                let address = await resolver.resolve4(name);
                if(address !== null){
                    return countryOf(address[0])
                }
                return 'unknown'
            }catch(e){
                return 'unknown'
            }
        }else{
            return 'unknown'
        }
    }
}
