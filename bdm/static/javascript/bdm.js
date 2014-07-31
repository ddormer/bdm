var servers = [
    ['125.63.61.79', 27015, 'AU'],
    ['74.91.122.222', 27015, 'US'],
    ['5.135.153.162', 27055, 'EU'],
    ['132.147.92.100', 28000, 'SG'],

    ['108.61.227.96', 27015, 'AU'],
    ['8.6.74.53', 27015, 'US'],
    ['41.86.100.101', 27015, 'ZA']];

var Throbber = React.createClass({
    render: function () {
        return React.DOM.img({className:'throbber', src:'static/images/throbber.gif'});
    }
});

var ServerStatus = React.createClass({
    render: function () {
        return React.DOM.div({},
            ServerList({servers:servers, url:'api/servers', pollInterval:20})
        );
    }
});

var Server = React.createClass({
    render: function() {
        var flag = "static/images/flags/"+this.props.server.location+".png";

        if (this.props.server.online) {
            return (
            React.DOM.div({className:"server-status server-up"}, [
                React.DOM.span({className:"server-players"},
                    React.DOM.span({className:"server-players-text"},
                        this.props.server.player_count+'/'+this.props.server.max_players
                    )
                ),
                React.DOM.span({className:"server-name"},
                    React.DOM.span({className:"server-name-text"},
                        this.props.server.server_name
                    )
                ),
                React.DOM.img({className:"server-location", src:flag, height:"40", width:"57"})]
            ));
        }
        else {
            return React.DOM.div({className:"server-status server-down"},
                       React.DOM.span({className:"server-name"}, this.props.server.server_name)
                   );
        }
    }
});

var ServerList = React.createClass({
    getInitialState: function() {
        return {data: []};
    },

    dataReceived: function(data) {
        this.setState({data: data.result});
    },

    serverError: function(xhr, status, err) {
        console.error(this.props.url, status, xhr);
    },

    queryServer: function() {
        $.ajax({
            data: JSON.stringify(this.props.servers),
            type: 'POST',
            url: this.props.url,
            dataType: 'json',
            success: this.dataReceived,
            error: this.serverError
        });
    },

    componentWillMount: function() {
        this.queryServer();
        if (this.props.pollInterval > 0) {
            setInterval(this.queryServer, this.props.pollInterval * 1000);
        }
    },

    render: function() {
        var serverNodes = this.state.data.map(function (server) {
            return Server({server:server});
        });
        if (serverNodes.length === 0) {
            return Throbber();
        }
        return React.DOM.div({}, serverNodes);
    }
});

var DonationList = React.createClass({
    render: function() {
        var donationNodes = this.props.data.map(function (donation) {
            return Donation({key:donation.date, donator:donation.personaname,
                             amount:donation.amount, avatar:donation.avatar});
        });
        if (donationNodes.length === 0) {
            return (
                React.DOM.div({className:"donation-list"}, [
                    React.DOM.div({className:"donation-list-title"}, [
                        React.DOM.span({className:"fa fa-trophy donation-list-icon"}),
                        this.props.title
                    ]),
                    Throbber()
                ]));
        }
        return (
            React.DOM.div({className:"donation-list"}, [
                React.DOM.div({className:"donation-list-title"}, [
                    React.DOM.span({className:"fa fa-trophy donation-list-icon"}),
                    this.props.title
                ]),
                donationNodes]
            )
        );
    }
});

var Donation = React.createClass({
    render: function() {
        if (!this.props.avatar) {
            this.props.avatar = 'static/images/default_avatar.png';
        }
        return (
            React.DOM.div({className:"donation"}, [
                React.DOM.img({className:"steam-avatar", src:this.props.avatar, height:"34", width:"34"}),
                React.DOM.div({className:"donator-name"}, this.props.donator),
                React.DOM.div({className:"donation-amount"}, '$'+this.props.amount)
            ])
        );
    }
});

var DonationBox = React.createClass({
    getInitialState: function() {
        return {data: []};
    },
    loadDonationsFromServer: function() {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function(data) {
                this.setState({data: data.result});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, xhr);
            }.bind(this)
        });
    },
    componentWillMount: function() {
        this.loadDonationsFromServer();
        if (this.props.pollInterval > 0) {
            setInterval(this.loadDonationsFromServer, this.props.pollInterval * 1000);
        }
    },

    render: function () {
        return DonationList({title:this.props.title, data:this.state.data});
    }
});

var DonationContainer = React.createClass({
    render: function () {
        return React.DOM.div({}, [
            DonationBox({title:"Leaderboard", url:"api/top", pollInterval:0}),
            DonationBox({title:"Recent", url:"api/recent", pollInterval:0})
        ]);
    }
});


React.renderComponent(
    DonationContainer(),
    document.getElementById('donation-container'));
React.renderComponent(
    ServerStatus(),
    document.getElementById('server-status-container'));
